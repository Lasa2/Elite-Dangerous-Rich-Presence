use super::models::{
    DiscordRichPresenceFields, ExecutablePath, LaunchMethod, LogLevel, Settings,
};

impl Default for Settings {
    fn default() -> Self {
        Self {
            start_to_tray: false,
            close_with_game: false,
            check_for_updates: true,
            start_app_with_system: false,
            game_directory: default_journal_path(),
            log_level: LogLevel::Info,
            discord_fields: DiscordRichPresenceFields::default(),
            launch_method: LaunchMethod::Steam,
            executable_path: ExecutablePath::Steam,
            launch_arguments: String::new(),
            start_game_with_app: false,
        }
    }
}

fn default_journal_path() -> Option<std::path::PathBuf> {
    dirs::home_dir()
        .map(|p| p.join("Saved Games/Frontier Developments/Elite Dangerous"))
        .filter(|p| p.exists())
}
