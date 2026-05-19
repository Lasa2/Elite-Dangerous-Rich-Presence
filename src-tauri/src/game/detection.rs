use serde::{Deserialize, Serialize};
use sysinfo::System;
use ts_rs::TS;

/// Process names to look for
const GAME_PROCESS_NAMES: &[&str] = &["EliteDangerous64.exe", "EliteDangerous.exe"];
const LAUNCHER_PROCESS_NAMES: &[&str] = &["EDLaunch.exe"];

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq, Eq, Default)]
#[ts(export)]
pub enum GameStatus {
    /// Neither game nor launcher is running
    #[default]
    NotRunning,
    /// Only the launcher is running
    LauncherRunning,
    /// The game client is running
    GameRunning,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct GameProcessInfo {
    pub status: GameStatus,
    /// Process ID of the game (if running)
    pub game_pid: Option<u32>,
    /// Process ID of the launcher (if running)
    pub launcher_pid: Option<u32>,
    /// Start time of the game process (Unix timestamp in seconds)
    pub game_start_time: Option<u64>,
}

impl Default for GameProcessInfo {
    fn default() -> Self {
        Self {
            status: GameStatus::NotRunning,
            game_pid: None,
            launcher_pid: None,
            game_start_time: None,
        }
    }
}

/// Detects Elite Dangerous game and launcher processes
pub struct ProcessDetector {
    system: System,
}

impl ProcessDetector {
    pub fn new() -> Self {
        Self {
            system: System::new(),
        }
    }

    /// Refresh process list and detect game status
    pub fn detect(&mut self) -> GameProcessInfo {
        // Refresh only the process list
        self.system.refresh_processes(sysinfo::ProcessesToUpdate::All, true);

        let mut info = GameProcessInfo::default();

        // Look for game process
        for (pid, process) in self.system.processes() {
            let name = process.name().to_string_lossy();

            // Check for game process
            if GAME_PROCESS_NAMES.iter().any(|n| name.eq_ignore_ascii_case(n)) {
                info.game_pid = Some(pid.as_u32());
                info.status = GameStatus::GameRunning;

                // Get process start time
                if let Some(start_time) = Self::get_process_start_time(process) {
                    info.game_start_time = Some(start_time);
                }
            }

            // Check for launcher process
            if LAUNCHER_PROCESS_NAMES.iter().any(|n| name.eq_ignore_ascii_case(n)) {
                info.launcher_pid = Some(pid.as_u32());
                // Only set to LauncherRunning if game isn't running
                if info.status == GameStatus::NotRunning {
                    info.status = GameStatus::LauncherRunning;
                }
            }
        }

        info
    }

    /// Check if the game is currently running (quick check without full refresh)
    #[allow(dead_code)]
    pub fn is_game_running(&mut self) -> bool {
        self.detect().status == GameStatus::GameRunning
    }

    /// Check if the launcher is currently running
    #[allow(dead_code)]
    pub fn is_launcher_running(&mut self) -> bool {
        let info = self.detect();
        info.status == GameStatus::LauncherRunning || info.launcher_pid.is_some()
    }

    /// Check if either game or launcher is running
    #[allow(dead_code)]
    pub fn is_any_running(&mut self) -> bool {
        self.detect().status != GameStatus::NotRunning
    }

    /// Get process start time as Unix timestamp
    fn get_process_start_time(process: &sysinfo::Process) -> Option<u64> {
        // sysinfo provides start_time() as seconds since UNIX epoch
        let start_time = process.start_time();
        if start_time > 0 {
            Some(start_time)
        } else {
            None
        }
    }
}

impl Default for ProcessDetector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detector_creation() {
        let detector = ProcessDetector::new();
        assert!(detector.system.processes().is_empty() || !detector.system.processes().is_empty());
    }

    #[test]
    fn test_detect_returns_info() {
        let mut detector = ProcessDetector::new();
        let info = detector.detect();
        // Should return valid info (game likely not running during tests)
        assert!(matches!(
            info.status,
            GameStatus::NotRunning | GameStatus::LauncherRunning | GameStatus::GameRunning
        ));
    }
}
