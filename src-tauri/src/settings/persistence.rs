use std::path::PathBuf;
use tauri::{path::BaseDirectory, Manager};

use super::models::Settings;

impl Settings {
    fn settings_file_path(app: &tauri::AppHandle) -> PathBuf {
        app.path()
            .resolve("settings.json", BaseDirectory::AppConfig)
            .unwrap_or_else(|e| {
                log::error!("Failed to resolve settings file path: {}", e);
                PathBuf::from("settings.json")
            })
    }

    pub fn load_from_disk(app: &tauri::AppHandle) -> Self {
        let config_path = Self::settings_file_path(app);

        if std::fs::exists(&config_path).is_ok() {
            match std::fs::read_to_string(&config_path) {
                Ok(contents) => match serde_json::from_str::<Settings>(&contents) {
                    Ok(settings) => settings,
                    Err(e) => {
                        log::error!("Failed to parse settings file: {}", e);
                        Settings::default()
                    }
                },
                Err(e) => {
                    log::error!("Failed to read settings file: {}", e);
                    Settings::default()
                }
            }
        } else {
            Settings::default()
        }
    }

    pub fn save_to_disk(&self, app: &tauri::AppHandle) -> Result<(), String> {
        let contents = serde_json::to_string_pretty(self).map_err(|e| {
            let msg = format!("Failed to serialize settings: {}", e);
            log::error!("{}", msg);
            msg
        })?;

        std::fs::write(Self::settings_file_path(app), contents).map_err(|e| {
            let msg = format!("Failed to write settings file: {}", e);
            log::error!("{}", msg);
            msg
        })?;

        Ok(())
    }
}
