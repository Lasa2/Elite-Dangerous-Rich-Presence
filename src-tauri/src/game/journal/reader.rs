use std::fs::File;
use std::io::{BufRead, BufReader, Seek, SeekFrom};
use std::path::{Path, PathBuf};

use thiserror::Error;

use super::events::JournalEvent;
use super::parser::{JournalParser, ParseResult, ParserStats};

/// Errors that can occur during journal reading
#[derive(Debug, Error)]
pub enum ReaderError {
    #[error("Failed to open journal file: {0}")]
    FileOpen(#[from] std::io::Error),

    #[error("Journal file not found: {0}")]
    FileNotFound(PathBuf),
}

/// Journal reader that reads entries from a journal file.
///
/// Supports:
/// - Reading all existing entries
/// - Incremental reading (polling for new lines)
/// - Session-aware reading (stops on Shutdown/Continued events)
pub struct JournalReader {
    /// Current journal file path
    file_path: PathBuf,
    /// Parser for journal lines
    parser: JournalParser,
    /// Current position in the file (byte offset)
    file_position: u64,
    /// Whether we've seen a session-ending event (Shutdown/Continued)
    session_ended: bool,
}

impl JournalReader {
    /// Create a new journal reader for the given file
    pub fn new(file_path: PathBuf) -> Self {
        Self {
            file_path,
            parser: JournalParser::new(),
            file_position: 0,
            session_ended: false,
        }
    }

    /// Get the current file path
    pub fn file_path(&self) -> &Path {
        &self.file_path
    }

    /// Check if the session has ended (Shutdown or Continued event seen)
    pub fn session_ended(&self) -> bool {
        self.session_ended
    }

    /// Read all existing entries from the journal file.
    /// Updates the file position to the end.
    pub fn read_all(&mut self) -> Result<Vec<ParseResult>, ReaderError> {
        if !self.file_path.exists() {
            return Err(ReaderError::FileNotFound(self.file_path.clone()));
        }

        let file = File::open(&self.file_path)?;
        let reader = BufReader::new(file);
        let mut results = Vec::new();

        for line in reader.lines() {
            match line {
                Ok(line) => {
                    let result = self.parser.parse_line(&line);

                    // Check for session-ending events
                    if let Some(ref event) = result.event {
                        if matches!(event, JournalEvent::Shutdown { .. } | JournalEvent::Continued { .. }) {
                            self.session_ended = true;
                        }
                    }

                    results.push(result);
                }
                Err(e) => {
                    log::warn!("Error reading journal line: {}", e);
                }
            }
        }

        // Update file position to end
        self.file_position = std::fs::metadata(&self.file_path)?.len();

        Ok(results)
    }

    /// Read new entries since last read (polling-based).
    /// Returns empty vec if no new content or session has ended.
    pub fn read_new(&mut self) -> Result<Vec<ParseResult>, ReaderError> {
        // Don't read more if session has ended
        if self.session_ended {
            return Ok(Vec::new());
        }

        if !self.file_path.exists() {
            return Err(ReaderError::FileNotFound(self.file_path.clone()));
        }

        let mut file = File::open(&self.file_path)?;
        let current_size = file.metadata()?.len();

        // No new content
        if current_size <= self.file_position {
            return Ok(Vec::new());
        }

        // Seek to last known position
        file.seek(SeekFrom::Start(self.file_position))?;

        let reader = BufReader::new(file);
        let mut results = Vec::new();

        for line in reader.lines() {
            match line {
                Ok(line) => {
                    if !line.trim().is_empty() {
                        let result = self.parser.parse_line(&line);

                        // Check for session-ending events
                        if let Some(ref event) = result.event {
                            if matches!(event, JournalEvent::Shutdown { .. } | JournalEvent::Continued { .. }) {
                                self.session_ended = true;
                            }
                        }

                        results.push(result);
                    }
                }
                Err(e) => {
                    log::warn!("Error reading new journal line: {}", e);
                }
            }
        }

        // Update position
        self.file_position = current_size;

        Ok(results)
    }

    /// Read only the events we care about (filtering out Unknown and errors)
    pub fn read_relevant_events(&mut self) -> Result<Vec<JournalEvent>, ReaderError> {
        let results = self.read_all()?;
        Ok(results
            .into_iter()
            .filter_map(|r| r.event)
            .filter(|e| !matches!(e, JournalEvent::Unknown))
            .collect())
    }

    /// Switch to a new journal file (e.g., when Continued event signals file switch)
    pub fn switch_file(&mut self, new_path: PathBuf) {
        log::info!("Switching to new journal file: {}", new_path.display());
        self.file_path = new_path;
        self.file_position = 0;
        self.session_ended = false;
        self.parser.reset_stats();
    }

    /// Reset for a new session (same file, read from beginning)
    pub fn reset(&mut self) {
        self.file_position = 0;
        self.session_ended = false;
        self.parser.reset_stats();
    }

    /// Get parser statistics
    pub fn stats(&self) -> ParserStats {
        self.parser.stats()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_reader_empty_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("Journal.2024-01-15T100000.01.log");
        File::create(&file_path).unwrap();

        let mut reader = JournalReader::new(file_path);
        let results = reader.read_all().unwrap();
        assert!(results.is_empty());
        assert!(!reader.session_ended());
    }

    #[test]
    fn test_reader_with_content() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("Journal.2024-01-15T100000.01.log");

        {
            let mut file = File::create(&file_path).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:00Z","event":"Fileheader","gameversion":"4.0"}}"#).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:01Z","event":"LoadGame","Commander":"Test","Ship":"Sidewinder","GameMode":"Solo"}}"#).unwrap();
        }

        let mut reader = JournalReader::new(file_path);
        let results = reader.read_all().unwrap();

        assert_eq!(results.len(), 2);
        assert!(results[0].event.is_some());
        assert!(results[1].event.is_some());
        assert!(!reader.session_ended());
    }

    #[test]
    fn test_reader_detects_shutdown() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("Journal.2024-01-15T100000.01.log");

        {
            let mut file = File::create(&file_path).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:00Z","event":"Fileheader"}}"#).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:01Z","event":"Shutdown"}}"#).unwrap();
        }

        let mut reader = JournalReader::new(file_path);
        let _ = reader.read_all().unwrap();

        assert!(reader.session_ended());
    }

    #[test]
    fn test_reader_incremental() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("Journal.2024-01-15T100000.01.log");

        // Create initial content
        {
            let mut file = File::create(&file_path).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:00Z","event":"Fileheader"}}"#).unwrap();
        }

        let mut reader = JournalReader::new(file_path.clone());

        // Read initial
        let results = reader.read_all().unwrap();
        assert_eq!(results.len(), 1);

        // Append new content
        {
            let mut file = std::fs::OpenOptions::new()
                .append(true)
                .open(&file_path)
                .unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:01Z","event":"LoadGame","Commander":"Test","Ship":"Sidewinder","GameMode":"Solo"}}"#).unwrap();
        }

        // Read new only
        let new_results = reader.read_new().unwrap();
        assert_eq!(new_results.len(), 1);

        // No more new content
        let empty_results = reader.read_new().unwrap();
        assert!(empty_results.is_empty());
    }

    #[test]
    fn test_reader_stops_after_shutdown() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("Journal.2024-01-15T100000.01.log");

        {
            let mut file = File::create(&file_path).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:00Z","event":"Fileheader"}}"#).unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:01Z","event":"Shutdown"}}"#).unwrap();
        }

        let mut reader = JournalReader::new(file_path.clone());
        let _ = reader.read_all().unwrap();
        assert!(reader.session_ended());

        // Append more content after shutdown
        {
            let mut file = std::fs::OpenOptions::new()
                .append(true)
                .open(&file_path)
                .unwrap();
            writeln!(file, r#"{{"timestamp":"2024-01-15T10:00:02Z","event":"Fileheader"}}"#).unwrap();
        }

        // Should not read new content after session ended
        let new_results = reader.read_new().unwrap();
        assert!(new_results.is_empty());
    }
}
