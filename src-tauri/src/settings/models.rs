use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use ts_rs::TS;

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

impl From<LogLevel> for log::LevelFilter {
    fn from(level: LogLevel) -> Self {
        match level {
            LogLevel::Trace => log::LevelFilter::Trace,
            LogLevel::Debug => log::LevelFilter::Debug,
            LogLevel::Info => log::LevelFilter::Info,
            LogLevel::Warn => log::LevelFilter::Warn,
            LogLevel::Error => log::LevelFilter::Error,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, TS, PartialEq, Eq)]
#[ts(export)]
pub enum LaunchMethod {
    Steam,
    EpicGames,
    Executable,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
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

impl Default for DiscordRichPresenceFields {
    fn default() -> Self {
        Self {
            commander: true,
            superpower: true,
            location: true,
            gamemode: true,
            multicrew_mode: false,
            multicrew_size: false,
            time_elapsed: true,
            ship_icon: true,
            ship_text: true,
        }
    }
}

pub const STEAM_URL: &str = "steam://launch/359320";
pub const EPIC_GAMES_URL: &str =
    "com.epicgames.launcher://apps/9c203b6ed35846e8a4a9ff1e314f6593?action=launch&silent=true";

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub enum ExecutablePath {
    Steam,
    EpicGames,
    Custom(PathBuf),
    None,
}

impl ExecutablePath {
    pub fn url_scheme(&self) -> Option<String> {
        match self {
            ExecutablePath::Steam => Some(STEAM_URL.to_string()),
            ExecutablePath::EpicGames => Some(EPIC_GAMES_URL.to_string()),
            ExecutablePath::Custom(path) => Some(path.to_string_lossy().to_string()),
            ExecutablePath::None => None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct Settings {
    pub start_to_tray: bool,
    pub close_with_game: bool,
    pub check_for_updates: bool,
    pub start_app_with_system: bool,

    pub game_directory: Option<PathBuf>,
    pub log_level: LogLevel,

    pub discord_fields: DiscordRichPresenceFields,

    pub launch_method: LaunchMethod,
    pub executable_path: ExecutablePath,
    pub launch_arguments: String,
    pub start_game_with_app: bool,
}
