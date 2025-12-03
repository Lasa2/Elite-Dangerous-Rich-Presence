use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tracing::error;
use ts_rs::TS;

use crate::util::get_data_dir;

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

impl LogLevel {
    pub fn as_filter_str(&self) -> &'static str {
        match self {
            LogLevel::Trace => "trace",
            LogLevel::Debug => "debug",
            LogLevel::Info => "info",
            LogLevel::Warn => "warn",
            LogLevel::Error => "error",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub enum LaunchMethod {
    Steam,
    EpicGames,
    Executable,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, TS)]
#[ts(export)]
pub struct DiscordRichPresenceFields {
    pub commander: bool,
    pub superpower: bool,
    pub location: bool,
    pub gamemode: bool,
    pub multicrew_mode: bool,
    pub multicrew_size: bool,
    pub time_elapsed: bool,
    pub ship_icon: bool,
    pub ship_text: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct Settings {
    pub start_to_tray: bool,
    pub close_with_game: bool,
    pub check_for_updates: bool,
    pub launch_on_system_startup: bool,

    pub game_directory: Option<PathBuf>,
    pub log_level: LogLevel,

    pub discord_fields: DiscordRichPresenceFields,

    pub launch_method: LaunchMethod,
    pub executable_path: Option<PathBuf>,
    pub launch_arguments: String,
    pub auto_start_game_on_app_start: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            start_to_tray: true,
            close_with_game: true,
            check_for_updates: true,
            launch_on_system_startup: false,
            game_directory: None,
            log_level: LogLevel::Info,
            discord_fields: DiscordRichPresenceFields::default(),
            launch_method: LaunchMethod::Steam,
            executable_path: None,
            launch_arguments: String::new(),
            auto_start_game_on_app_start: false,
        }
    }
}

impl Settings {
    fn settings_file_path() -> PathBuf {
        let config_dir = get_data_dir();
        config_dir.join("settings.json")
    }

    pub fn load_from_disk() -> Self {
        let config_path = Self::settings_file_path();

        if std::fs::exists(&config_path).is_ok() {
            match std::fs::read_to_string(&config_path) {
                Ok(contents) => match serde_json::from_str::<Settings>(&contents) {
                    Ok(settings) => settings,
                    Err(e) => {
                        error!("Failed to parse settings file: {}", e);
                        Settings::default()
                    }
                },
                Err(e) => {
                    error!("Failed to read settings file: {}", e);
                    Settings::default()
                }
            }
        } else {
            Settings::default()
        }
    }

    pub fn save_to_disk(&self) -> Result<(), ()> {
        let contents = serde_json::to_string_pretty(self).map_err(|e| {
            error!("Failed to serialize settings: {}", e);
        })?;

        std::fs::write(Self::settings_file_path(), contents).map_err(|e| {
            error!("Failed to write settings file: {}", e);
        })?;

        Ok(())
    }
}

#[cfg(test)]
mod ts_export {
    use super::*;

    #[test]
    fn export_ts() {
        // The derives + #[ts(export,...)] are enough; referencing the types
        // here ensures the codegen runs.
        let _ = LogLevel::Info;
        let _ = LaunchMethod::Steam;
        let _ = Settings::default();
        let _ = DiscordRichPresenceFields::default();
    }
}
