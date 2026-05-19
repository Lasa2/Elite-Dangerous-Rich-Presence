use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;
use ts_rs::TS;

use super::events::JournalEvent;

/// Errors that can occur during journal parsing
#[derive(Debug, Error)]
pub enum ParseError {
    #[error("Invalid JSON: {0}")]
    InvalidJson(#[from] serde_json::Error),

    #[error("Missing 'event' field in journal entry")]
    MissingEventField,

    #[error("Empty line")]
    EmptyLine,
}

/// Result of parsing a single journal line
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ParseResult {
    /// The parsed event, if successful
    pub event: Option<JournalEvent>,
    /// The raw event type name (useful for unknown events)
    pub event_type: Option<String>,
    /// Error message if parsing failed
    pub error: Option<String>,
    /// The raw JSON line (useful for debugging)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub raw: Option<String>,
}

impl ParseResult {
    pub fn success(event: JournalEvent) -> Self {
        Self {
            event_type: Some(event.event_type().to_string()),
            event: Some(event),
            error: None,
            raw: None,
        }
    }

    pub fn unknown_event(event_type: String, raw: String) -> Self {
        Self {
            event: Some(JournalEvent::Unknown),
            event_type: Some(event_type),
            error: None,
            raw: Some(raw),
        }
    }

    pub fn error(error: String, raw: Option<String>) -> Self {
        Self {
            event: None,
            event_type: None,
            error: Some(error),
            raw,
        }
    }
}

/// Journal parser with lenient parsing and error recovery
pub struct JournalParser {
    /// Count of successfully parsed events
    pub success_count: usize,
    /// Count of unknown events (parsed but not recognized)
    pub unknown_count: usize,
    /// Count of parse errors
    pub error_count: usize,
}

impl JournalParser {
    pub fn new() -> Self {
        Self {
            success_count: 0,
            unknown_count: 0,
            error_count: 0,
        }
    }

    /// Parse a single line from a journal file.
    /// Returns a ParseResult that always succeeds (errors are captured in the result).
    pub fn parse_line(&mut self, line: &str) -> ParseResult {
        let trimmed = line.trim();

        // Skip empty lines
        if trimmed.is_empty() {
            return ParseResult::error("Empty line".to_string(), None);
        }

        // First, try to parse as raw JSON to get the event type
        let raw_value: Value = match serde_json::from_str(trimmed) {
            Ok(v) => v,
            Err(e) => {
                self.error_count += 1;
                log::warn!("Failed to parse journal line as JSON: {}", e);
                return ParseResult::error(
                    format!("Invalid JSON: {}", e),
                    Some(trimmed.to_string()),
                );
            }
        };

        // Extract the event type for logging/debugging
        let event_type = raw_value
            .get("event")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        if event_type.is_none() {
            self.error_count += 1;
            log::warn!("Journal entry missing 'event' field: {}", trimmed);
            return ParseResult::error(
                "Missing 'event' field".to_string(),
                Some(trimmed.to_string()),
            );
        }

        let event_type_str = event_type.clone().unwrap();

        // Now try to parse as a typed JournalEvent
        match serde_json::from_str::<JournalEvent>(trimmed) {
            Ok(event) => {
                if matches!(event, JournalEvent::Unknown) {
                    // Parsed successfully but as Unknown
                    self.unknown_count += 1;
                    log::trace!("Unknown journal event type: {}", event_type_str);
                    ParseResult::unknown_event(event_type_str, trimmed.to_string())
                } else {
                    self.success_count += 1;
                    log::trace!("Parsed journal event: {}", event_type_str);
                    ParseResult::success(event)
                }
            }
            Err(e) => {
                // This shouldn't happen often since we have #[serde(other)] for Unknown
                // But it can happen if a known event type has unexpected field types
                self.error_count += 1;
                log::warn!(
                    "Failed to parse known event type '{}': {} - falling back to Unknown",
                    event_type_str,
                    e
                );
                ParseResult::unknown_event(event_type_str, trimmed.to_string())
            }
        }
    }

    /// Parse multiple lines from a journal file
    pub fn parse_lines(&mut self, content: &str) -> Vec<ParseResult> {
        content
            .lines()
            .filter(|line| !line.trim().is_empty())
            .map(|line| self.parse_line(line))
            .collect()
    }

    /// Get parsing statistics
    pub fn stats(&self) -> ParserStats {
        ParserStats {
            success_count: self.success_count,
            unknown_count: self.unknown_count,
            error_count: self.error_count,
        }
    }

    /// Reset statistics
    pub fn reset_stats(&mut self) {
        self.success_count = 0;
        self.unknown_count = 0;
        self.error_count = 0;
    }
}

impl Default for JournalParser {
    fn default() -> Self {
        Self::new()
    }
}

/// Parser statistics
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ParserStats {
    pub success_count: usize,
    pub unknown_count: usize,
    pub error_count: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_valid_event() {
        let mut parser = JournalParser::new();
        let line = r#"{"timestamp":"2024-01-15T10:30:00Z","event":"Shutdown"}"#;
        let result = parser.parse_line(line);

        assert!(result.event.is_some());
        assert!(result.error.is_none());
        assert_eq!(parser.success_count, 1);
    }

    #[test]
    fn test_parse_unknown_event() {
        let mut parser = JournalParser::new();
        let line = r#"{"timestamp":"2024-01-15T10:30:00Z","event":"SomeFutureEvent"}"#;
        let result = parser.parse_line(line);

        assert!(result.event.is_some());
        assert!(matches!(result.event.as_ref().unwrap(), JournalEvent::Unknown));
        assert_eq!(result.event_type, Some("SomeFutureEvent".to_string()));
        assert_eq!(parser.unknown_count, 1);
    }

    #[test]
    fn test_parse_invalid_json() {
        let mut parser = JournalParser::new();
        let line = "this is not json";
        let result = parser.parse_line(line);

        assert!(result.event.is_none());
        assert!(result.error.is_some());
        assert_eq!(parser.error_count, 1);
    }

    #[test]
    fn test_parse_empty_line() {
        let mut parser = JournalParser::new();
        let result = parser.parse_line("   ");

        assert!(result.event.is_none());
        assert!(result.error.is_some());
    }
}
