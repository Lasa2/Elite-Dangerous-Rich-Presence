use std::fs;
use std::path::{Path, PathBuf};

use chrono::{DateTime, NaiveDateTime, Utc};
use regex::Regex;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use ts_rs::TS;

/// Errors that can occur during journal discovery
#[derive(Debug, Error)]
pub enum DiscoveryError {
    #[error("Journal directory not found: {0}")]
    DirectoryNotFound(PathBuf),

    #[error("Failed to read directory: {0}")]
    ReadError(#[from] std::io::Error),

    #[error("No journal files found")]
    NoJournalsFound,

    #[error("Game just started, waiting for journal file")]
    WaitingForJournal,
}

/// Information about a discovered journal file
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct JournalFileInfo {
    /// Full path to the journal file
    pub path: PathBuf,
    /// Filename without directory
    pub filename: String,
    /// Timestamp extracted from filename
    pub timestamp: Option<i64>,
    /// Part number (for multi-part journals)
    pub part: Option<u32>,
}

/// Journal file discovery utility
pub struct JournalDiscovery {
    /// Base directory where journal files are stored
    journal_dir: PathBuf,
    /// Regex for new-style journal filenames: Journal.YYYY-MM-DDThhmmss.NN.log
    new_format_regex: Regex,
    /// Regex for old-style journal filenames: Journal.YYMMDDhhmmss.NN.log
    old_format_regex: Regex,
}

impl JournalDiscovery {
    /// Create a new journal discovery instance with the given journal directory
    pub fn new(journal_dir: PathBuf) -> Self {
        Self {
            journal_dir,
            // New format: Journal.2024-01-15T103045.01.log
            new_format_regex: Regex::new(
                r"^Journal\.(\d{4}-\d{2}-\d{2}T\d{6})\.(\d{2})\.log$"
            ).expect("Invalid regex"),
            // Old format: Journal.240115103045.01.log (legacy)
            old_format_regex: Regex::new(
                r"^Journal\.(\d{12})\.(\d{2})\.log$"
            ).expect("Invalid regex"),
        }
    }

    /// Create with the default Elite Dangerous journal directory
    pub fn with_default_dir() -> Option<Self> {
        Self::default_journal_dir().map(Self::new)
    }

    /// Get the default Elite Dangerous journal directory
    pub fn default_journal_dir() -> Option<PathBuf> {
        // Windows: %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous
        if cfg!(windows) {
            dirs::home_dir().map(|home| {
                home.join("Saved Games")
                    .join("Frontier Developments")
                    .join("Elite Dangerous")
            })
        } else if cfg!(target_os = "linux") {
            // Linux (Proton): ~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous
            dirs::data_local_dir().map(|data| {
                data.join("Steam")
                    .join("steamapps")
                    .join("compatdata")
                    .join("359320")
                    .join("pfx")
                    .join("drive_c")
                    .join("users")
                    .join("steamuser")
                    .join("Saved Games")
                    .join("Frontier Developments")
                    .join("Elite Dangerous")
            })
        } else {
            None
        }
    }

    /// Find all journal files in the directory
    pub fn find_all(&self) -> Result<Vec<JournalFileInfo>, DiscoveryError> {
        if !self.journal_dir.exists() {
            return Err(DiscoveryError::DirectoryNotFound(self.journal_dir.clone()));
        }

        let mut journals = Vec::new();

        for entry in fs::read_dir(&self.journal_dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() {
                if let Some(info) = self.parse_journal_filename(&path) {
                    journals.push(info);
                }
            }
        }

        // Sort by timestamp (newest first)
        journals.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));

        Ok(journals)
    }

    /// Find the newest journal file
    pub fn find_newest(&self) -> Result<JournalFileInfo, DiscoveryError> {
        let journals = self.find_all()?;
        journals.into_iter().next().ok_or(DiscoveryError::NoJournalsFound)
    }

    /// Find the journal file for the current game session.
    ///
    /// Logic:
    /// - If game is running: find the journal that was created around game start time
    /// - If game just started (no journal yet): return None via NoJournalsFound
    /// - If no game start time provided: return the newest journal
    ///
    /// The journal file is typically created shortly after the game process starts,
    /// but there can be a delay of several seconds.
    pub fn find_for_session(&self, game_start_time: Option<u64>) -> Result<JournalFileInfo, DiscoveryError> {
        let journals = self.find_all()?;

        if journals.is_empty() {
            return Err(DiscoveryError::NoJournalsFound);
        }

        // If no game start time provided, return newest
        let Some(game_start_time) = game_start_time else {
            return journals.into_iter().next().ok_or(DiscoveryError::NoJournalsFound);
        };

        let game_start_time = game_start_time as i64;

        // The journal file is created after the game process starts.
        // We want to find the journal whose timestamp is:
        // 1. At or after the game start time (journal created after process)
        // 2. Or within a small window before (in case of clock skew)
        //
        // But NOT a journal from a much older session.

        // Allow 30 seconds before game start for clock skew
        let earliest_valid = game_start_time - 30;
        // Allow up to 5 minutes after game start for journal creation delay
        let latest_valid = game_start_time + 300;

        // Journals are sorted newest first, so find the first one that fits our session
        // We want the NEWEST journal that was created around or after game start
        for journal in &journals {
            if let Some(timestamp) = journal.timestamp {
                // Journal must be created around the time the game started
                if timestamp >= earliest_valid && timestamp <= latest_valid {
                    return Ok(journal.clone());
                }
                // If journal is newer than our window, it might be from a future session
                // (shouldn't happen, but skip it)
                if timestamp > latest_valid {
                    continue;
                }
                // If journal is older than our window, this and all following are too old
                if timestamp < earliest_valid {
                    break;
                }
            }
        }

        // No journal found for this session - game may have just started
        // Return an error so caller knows to wait/retry
        Err(DiscoveryError::NoJournalsFound)
    }

    /// Find the journal file for the current session, or return the newest if no match.
    /// Use this when you want a fallback to the newest journal.
    pub fn find_for_session_or_newest(&self, game_start_time: Option<u64>) -> Result<JournalFileInfo, DiscoveryError> {
        match self.find_for_session(game_start_time) {
            Ok(journal) => Ok(journal),
            Err(DiscoveryError::NoJournalsFound) if game_start_time.is_some() => {
                // No session-matched journal, fall back to newest
                log::debug!("No journal found for session, falling back to newest");
                self.find_newest()
            }
            Err(e) => Err(e),
        }
    }

    /// Parse a journal filename and extract metadata
    fn parse_journal_filename(&self, path: &Path) -> Option<JournalFileInfo> {
        let filename = path.file_name()?.to_str()?;

        // Try new format first
        if let Some(caps) = self.new_format_regex.captures(filename) {
            let datetime_str = caps.get(1)?.as_str();
            let part_str = caps.get(2)?.as_str();

            // Parse datetime: 2024-01-15T103045
            let timestamp = NaiveDateTime::parse_from_str(datetime_str, "%Y-%m-%dT%H%M%S")
                .ok()
                .map(|dt| DateTime::<Utc>::from_naive_utc_and_offset(dt, Utc).timestamp());

            let part = part_str.parse().ok();

            return Some(JournalFileInfo {
                path: path.to_path_buf(),
                filename: filename.to_string(),
                timestamp,
                part,
            });
        }

        // Try old/legacy format
        if let Some(caps) = self.old_format_regex.captures(filename) {
            let datetime_str = caps.get(1)?.as_str();
            let part_str = caps.get(2)?.as_str();

            // Parse datetime: YYMMDDhhmmss (e.g., 240115103045)
            let timestamp = NaiveDateTime::parse_from_str(datetime_str, "%y%m%d%H%M%S")
                .ok()
                .map(|dt| DateTime::<Utc>::from_naive_utc_and_offset(dt, Utc).timestamp());

            let part = part_str.parse().ok();

            return Some(JournalFileInfo {
                path: path.to_path_buf(),
                filename: filename.to_string(),
                timestamp,
                part,
            });
        }

        None
    }

    /// Get the journal directory path
    pub fn journal_dir(&self) -> &Path {
        &self.journal_dir
    }

    /// Check if the journal directory exists
    pub fn directory_exists(&self) -> bool {
        self.journal_dir.exists()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_new_format_filename() {
        let discovery = JournalDiscovery::new(PathBuf::from("."));
        let path = PathBuf::from("Journal.2024-01-15T103045.01.log");
        let info = discovery.parse_journal_filename(&path);

        assert!(info.is_some());
        let info = info.unwrap();
        assert_eq!(info.filename, "Journal.2024-01-15T103045.01.log");
        assert!(info.timestamp.is_some());
        assert_eq!(info.part, Some(1));
    }

    #[test]
    fn test_parse_old_format_filename() {
        let discovery = JournalDiscovery::new(PathBuf::from("."));
        let path = PathBuf::from("Journal.240115103045.01.log");
        let info = discovery.parse_journal_filename(&path);

        assert!(info.is_some());
        let info = info.unwrap();
        assert_eq!(info.filename, "Journal.240115103045.01.log");
        assert!(info.timestamp.is_some());
        assert_eq!(info.part, Some(1));
    }

    #[test]
    fn test_parse_invalid_filename() {
        let discovery = JournalDiscovery::new(PathBuf::from("."));
        let path = PathBuf::from("not_a_journal.txt");
        let info = discovery.parse_journal_filename(&path);

        assert!(info.is_none());
    }

    #[test]
    fn test_default_journal_dir() {
        let dir = JournalDiscovery::default_journal_dir();
        // Should return Some on Windows, possibly None on other platforms
        if cfg!(windows) {
            assert!(dir.is_some());
            let dir = dir.unwrap();
            assert!(dir.to_string_lossy().contains("Frontier Developments"));
        }
    }
}
