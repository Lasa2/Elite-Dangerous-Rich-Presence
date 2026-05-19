use std::sync::Mutex;

use crate::error::{AppError, AppResult};
use crate::settings::{ExecutablePath, LaunchMethod, Settings};
use crate::system::autostart::set_autolaunch;

#[tauri::command]
pub fn get_settings(state: tauri::State<Mutex<Settings>>) -> Settings {
    log::trace!("Getting settings from backend");
    let s = match state.lock() {
        Ok(s) => s.clone(),
        Err(e) => {
            log::error!("Failed to lock settings mutex: {}", e);
            Settings::default()
        }
    };

    log::debug!("Returning settings: {:?}", s);
    s
}

#[tauri::command]
pub fn update_settings(
    app: tauri::AppHandle,
    state: tauri::State<Mutex<Settings>>,
    mut new_settings: Settings,
) -> AppResult<Settings> {
    log::trace!("Updating settings from backend: {:?}", new_settings);

    log::debug!("Validating new settings");
    // Validate paths
    if !new_settings.validate_game_directory() {
        let msg = format!(
            "Invalid game directory: {:?}",
            new_settings.game_directory
        );
        log::error!("{}", msg);
        return Err(AppError::InvalidGameDirectory(msg));
    }
    log::debug!(
        "Valid game directory: {:?}",
        new_settings.game_directory
    );

    // Validate executable path if launch method is Executable
    // If the launch method changed to Executable, we skip validation here to allow user to set it later
    let launch_method_changed = {
        let current_settings = state.lock().map_err(|_| AppError::SettingsLock)?;
        current_settings.launch_method != new_settings.launch_method
    };

    if new_settings.launch_method == LaunchMethod::Executable && !launch_method_changed {
        if !new_settings.validate_executable_path() {
            let msg = format!(
                "Invalid executable path for launch method Executable: {:?}",
                new_settings.executable_path
            );
            log::error!("{}", msg);
            return Err(AppError::InvalidExecutablePath(msg));
        }
    }

    // Set executable path based on launch method
    match new_settings.launch_method {
        LaunchMethod::Steam => {
            log::debug!("Setting executable path to Steam URL scheme");
            new_settings.executable_path = ExecutablePath::Steam;
        }
        LaunchMethod::EpicGames => {
            log::debug!("Setting executable path to Epic Games URL scheme");
            new_settings.executable_path = ExecutablePath::EpicGames;
        }
        LaunchMethod::Executable => {
            log::debug!(
                "Using custom executable path: {:?}",
                new_settings.executable_path
            );
            // If launch method changed to Executable, set to None to force user to set it
            if launch_method_changed {
                new_settings.executable_path = ExecutablePath::None;
            }
        }
    }

    // Update settings in state
    log::debug!("Updating settings in state");
    {
        let mut settings = state.lock().map_err(|_| AppError::SettingsLock)?;
        *settings = new_settings;
    }

    let settings = state.lock().map_err(|_| AppError::SettingsLock)?.clone();
    if let Err(e) = settings.save_to_disk(&app) {
        log::error!("Failed to save settings to disk: {:?}", e);
    } else {
        log::info!("Settings saved to disk successfully");
    }

    log::info!("Settings updated: {:?}", settings);
    log::set_max_level(settings.log_level.clone().into());
    set_autolaunch(&app, &state, settings.start_app_with_system);

    Ok(settings)
}

#[tauri::command]
pub fn reset_settings(
    app: tauri::AppHandle,
    state: tauri::State<Mutex<Settings>>,
) -> AppResult<Settings> {
    log::trace!("Resetting settings to default from backend");
    let default_settings = Settings::default();
    {
        let mut settings = state.lock().map_err(|_| AppError::SettingsLock)?;
        *settings = default_settings.clone();
    }

    let settings = state.lock().map_err(|_| AppError::SettingsLock)?.clone();
    if let Err(e) = settings.save_to_disk(&app) {
        log::error!("Failed to save settings to disk: {:?}", e);
    } else {
        log::info!("Settings saved to disk successfully");
    }

    log::info!("Settings reset to default: {:?}", settings);
    log::set_max_level(settings.log_level.clone().into());
    set_autolaunch(&app, &state, settings.start_app_with_system);

    Ok(settings)
}
