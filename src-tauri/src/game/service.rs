use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::{Arc, RwLock};
use std::thread::{self, JoinHandle};
use std::time::Duration;

use crossbeam_channel::{self as channel, Receiver, Sender};
use tauri::{AppHandle, Emitter, Manager};

use super::detection::{GameStatus, ProcessDetector};
use super::journal::{JournalDiscovery, JournalEvent};
use super::state::{ActivityStatus, GameState};
use crate::settings::Settings;

/// Interval for process detection polling
const PROCESS_POLL_INTERVAL: Duration = Duration::from_secs(2);
/// Sleep duration when journal reader hits EOF (no new content)
const READER_IDLE_SLEEP: Duration = Duration::from_millis(100);

/// Events emitted to the frontend
const EVENT_GAME_STATE_CHANGED: &str = "game-state-changed";
const EVENT_GAME_STATUS_CHANGED: &str = "game-status-changed";

/// Commands sent to the reader thread
#[derive(Debug)]
pub enum ReaderCommand {
    /// Start reading a journal file
    Start {
        path: PathBuf,
        #[allow(dead_code)]
        game_start_time: Option<u64>,
    },
    /// Stop reading (session ended or shutdown)
    Stop,
}

/// Events sent from reader to monitor
#[derive(Debug)]
pub enum ReaderEvent {
    /// Game state was updated from journal events
    StateUpdated(GameState),
    /// Session ended (Shutdown/Continued event seen)
    SessionEnded,
}

/// Shared state that can be queried by Tauri commands
#[derive(Debug, Default)]
pub struct ServiceState {
    pub status: GameStatus,
    pub game_state: GameState,
}

/// Handle to the running game service
pub struct GameService {
    /// Shared state for queries
    state: Arc<RwLock<ServiceState>>,
    /// Channel to signal shutdown
    shutdown_tx: Sender<()>,
    /// Monitor thread handle
    _monitor_handle: JoinHandle<()>,
    /// Reader thread handle
    _reader_handle: JoinHandle<()>,
}

impl GameService {
    /// Get the current game status
    pub fn status(&self) -> GameStatus {
        self.state
            .read()
            .map(|s| s.status.clone())
            .unwrap_or_default()
    }

    /// Get the current game state
    #[allow(dead_code)]
    pub fn game_state(&self) -> GameState {
        self.state
            .read()
            .map(|s| s.game_state.clone())
            .unwrap_or_default()
    }

    /// Request service shutdown
    #[allow(dead_code)]
    pub fn shutdown(&self) {
        let _ = self.shutdown_tx.send(());
    }
}

/// Shared handle type for Tauri state management
pub type SharedGameService = Arc<GameService>;

/// Create and start the game service
pub fn create_service(app: &AppHandle) -> SharedGameService {
    // Get journal directory from settings
    let journal_dir = {
        let settings = app.state::<std::sync::Mutex<Settings>>();
        let settings = settings.lock().unwrap();
        settings
            .game_directory
            .clone()
            .map(PathBuf::from)
            .or_else(JournalDiscovery::default_journal_dir)
            .unwrap_or_else(|| PathBuf::from("."))
    };

    log::info!("Journal directory: {}", journal_dir.display());

    // Create channels
    let (shutdown_tx, shutdown_rx) = channel::bounded::<()>(1);
    let (reader_cmd_tx, reader_cmd_rx) = channel::unbounded::<ReaderCommand>();
    let (reader_event_tx, reader_event_rx) = channel::unbounded::<ReaderEvent>();

    // Create shared state
    let state = Arc::new(RwLock::new(ServiceState::default()));

    // Clone for threads
    let app_handle = app.clone();
    let state_for_monitor = state.clone();

    // Spawn monitor thread
    let monitor_handle = thread::Builder::new()
        .name("game-monitor".to_string())
        .spawn(move || {
            monitor_thread(
                app_handle,
                state_for_monitor,
                journal_dir,
                shutdown_rx,
                reader_cmd_tx,
                reader_event_rx,
            );
        })
        .expect("Failed to spawn monitor thread");

    // Spawn reader thread
    let reader_handle = thread::Builder::new()
        .name("journal-reader".to_string())
        .spawn(move || {
            reader_thread(reader_cmd_rx, reader_event_tx);
        })
        .expect("Failed to spawn reader thread");

    Arc::new(GameService {
        state,
        shutdown_tx,
        _monitor_handle: monitor_handle,
        _reader_handle: reader_handle,
    })
}

/// Monitor thread - handles process detection and coordinates reader
fn monitor_thread(
    app: AppHandle,
    state: Arc<RwLock<ServiceState>>,
    journal_dir: PathBuf,
    shutdown_rx: Receiver<()>,
    reader_cmd_tx: Sender<ReaderCommand>,
    reader_event_rx: Receiver<ReaderEvent>,
) {
    log::info!("Monitor thread started");

    let mut detector = ProcessDetector::new();
    let mut last_status = GameStatus::NotRunning;
    let mut reader_active = false;

    loop {
        // Check shutdown signal (with timeout = poll interval)
        match shutdown_rx.recv_timeout(PROCESS_POLL_INTERVAL) {
            Ok(()) => {
                log::info!("Monitor thread received shutdown signal");
                let _ = reader_cmd_tx.send(ReaderCommand::Stop);
                break;
            }
            Err(channel::RecvTimeoutError::Disconnected) => {
                log::info!("Monitor thread: shutdown channel disconnected");
                let _ = reader_cmd_tx.send(ReaderCommand::Stop);
                break;
            }
            Err(channel::RecvTimeoutError::Timeout) => {
                // Normal - continue polling
            }
        }

        // Drain reader events (non-blocking)
        while let Ok(event) = reader_event_rx.try_recv() {
            match event {
                ReaderEvent::StateUpdated(game_state) => {
                    // Update shared state
                    if let Ok(mut s) = state.write() {
                        s.game_state = game_state.clone();
                    }
                    // Emit to frontend
                    log::debug!("Game state changed: {:?}", game_state.status);
                    if let Err(e) = app.emit(EVENT_GAME_STATE_CHANGED, &game_state) {
                        log::error!("Failed to emit game state event: {}", e);
                    }
                }
                ReaderEvent::SessionEnded => {
                    log::info!("Journal session ended");
                    reader_active = false;
                }
            }
        }

        // Check process status
        let info = detector.detect();
        let new_status = info.status.clone();

        if new_status != last_status {
            log::debug!("Process status changed: {:?} -> {:?}", last_status, new_status);

            // Handle transitions
            match (&last_status, &new_status) {
                // Game just started
                (_, GameStatus::GameRunning) if !reader_active => {
                    log::info!("Game started, looking for journal file...");

                    let discovery = JournalDiscovery::new(journal_dir.clone());
                    match discovery.find_for_session(info.game_start_time) {
                        Ok(journal_info) => {
                            log::info!("Found journal file: {}", journal_info.filename);
                            let _ = reader_cmd_tx.send(ReaderCommand::Start {
                                path: journal_info.path,
                                game_start_time: info.game_start_time,
                            });
                            reader_active = true;
                        }
                        Err(e) => {
                            log::warn!("Could not find journal for session: {}", e);
                            // Will retry on next poll
                        }
                    }
                }

                // Game stopped
                (GameStatus::GameRunning, _) => {
                    log::info!("Game stopped");
                    if reader_active {
                        let _ = reader_cmd_tx.send(ReaderCommand::Stop);
                        reader_active = false;
                    }

                    // Reset game state
                    if let Ok(mut s) = state.write() {
                        s.game_state.reset();
                        if new_status == GameStatus::LauncherRunning {
                            s.game_state.status = ActivityStatus::Launcher;
                            s.game_state.star_system = Some("Launcher".to_string());
                        }
                    }
                }

                // Launcher started from nothing
                (GameStatus::NotRunning, GameStatus::LauncherRunning) => {
                    log::info!("Launcher started");
                    if let Ok(mut s) = state.write() {
                        s.game_state.status = ActivityStatus::Launcher;
                        s.game_state.star_system = Some("Launcher".to_string());
                    }
                }

                _ => {}
            }

            // Update status in shared state
            if let Ok(mut s) = state.write() {
                s.status = new_status.clone();
            }

            // Emit status change to frontend
            if let Err(e) = app.emit(EVENT_GAME_STATUS_CHANGED, &new_status) {
                log::error!("Failed to emit game status event: {}", e);
            }

            // Also emit state if it changed (for launcher transitions)
            if let Ok(s) = state.read() {
                if let Err(e) = app.emit(EVENT_GAME_STATE_CHANGED, &s.game_state) {
                    log::error!("Failed to emit game state event: {}", e);
                }
            }

            last_status = new_status;
        }

        // If game is running but reader isn't active, try to start it
        if last_status == GameStatus::GameRunning && !reader_active {
            let discovery = JournalDiscovery::new(journal_dir.clone());
            if let Ok(journal_info) = discovery.find_for_session(info.game_start_time) {
                log::info!("Found journal file (retry): {}", journal_info.filename);
                let _ = reader_cmd_tx.send(ReaderCommand::Start {
                    path: journal_info.path,
                    game_start_time: info.game_start_time,
                });
                reader_active = true;
            }
        }
    }

    log::info!("Monitor thread stopped");
}

/// Reader thread - blocks reading journal file
fn reader_thread(cmd_rx: Receiver<ReaderCommand>, event_tx: Sender<ReaderEvent>) {
    log::info!("Reader thread started");

    loop {
        // Wait for start command (blocking)
        match cmd_rx.recv() {
            Ok(ReaderCommand::Start { path, .. }) => {
                log::info!("Reader starting: {}", path.display());
                read_journal_blocking(&path, &cmd_rx, &event_tx);
                log::info!("Reader finished session");
            }
            Ok(ReaderCommand::Stop) => {
                log::info!("Reader received stop command while idle");
                // Already idle, ignore
            }
            Err(_) => {
                log::info!("Reader thread: command channel disconnected");
                break;
            }
        }
    }

    log::info!("Reader thread stopped");
}

/// Read journal file in blocking mode until session ends
fn read_journal_blocking(path: &Path, cmd_rx: &Receiver<ReaderCommand>, event_tx: &Sender<ReaderEvent>) {
    // Open file with explicit sharing flags on Windows
    #[cfg(windows)]
    use std::os::windows::fs::OpenOptionsExt;

    let file = {
        let mut opts = std::fs::OpenOptions::new();
        opts.read(true);

        #[cfg(windows)]
        {
            // FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE = 0x7
            // Allows game to keep writing while we read
            opts.share_mode(0x7);
        }

        match opts.open(path) {
            Ok(f) => f,
            Err(e) => {
                log::error!("Failed to open journal file: {}", e);
                return;
            }
        }
    };

    let mut reader = BufReader::new(file);
    let mut state = GameState::new();
    let mut line = String::new();

    loop {
        // Check for stop command (non-blocking)
        match cmd_rx.try_recv() {
            Ok(ReaderCommand::Stop) => {
                log::info!("Reader received stop command");
                break;
            }
            Ok(ReaderCommand::Start { .. }) => {
                // Shouldn't happen, but ignore
                log::warn!("Reader received start command while already reading");
            }
            Err(channel::TryRecvError::Empty) => {
                // Normal - continue reading
            }
            Err(channel::TryRecvError::Disconnected) => {
                log::info!("Reader: command channel disconnected");
                break;
            }
        }

        // Try to read a line
        line.clear();
        match reader.read_line(&mut line) {
            Ok(0) => {
                // EOF - no new content, sleep briefly and retry
                thread::sleep(READER_IDLE_SLEEP);
                continue;
            }
            Ok(_) => {
                // Got a line - parse it
                let trimmed = line.trim();
                if trimmed.is_empty() {
                    continue;
                }

                match serde_json::from_str::<JournalEvent>(trimmed) {
                    Ok(event) => {
                        log::debug!("Journal event: {:?}", event);
                        state.process_event(&event);
                        let _ = event_tx.send(ReaderEvent::StateUpdated(state.clone()));

                        // Check for session end
                        if matches!(
                            event,
                            JournalEvent::Shutdown { .. } | JournalEvent::Continued { .. }
                        ) {
                            log::info!("Session ending event: {:?}", event);
                            let _ = event_tx.send(ReaderEvent::SessionEnded);
                            break;
                        }
                    }
                    Err(e) => {
                        // Not all lines are valid events we care about
                        log::trace!("Failed to parse journal line: {} - {}", e, trimmed);
                    }
                }
            }
            Err(e) => {
                log::error!("Error reading journal line: {}", e);
                thread::sleep(READER_IDLE_SLEEP);
            }
        }
    }
}
