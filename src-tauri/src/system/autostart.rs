use std::sync::Mutex;

use tauri_plugin_autostart::ManagerExt;

use crate::settings::Settings;

/// Set the system autolaunch state based on the desired state
/// Syncs the autolaunch setting in the Settings struct with the actual autolaunch state after changing it
pub fn set_autolaunch(
    app: &tauri::AppHandle,
    settings: &tauri::State<Mutex<Settings>>,
    desired_state: bool,
) {
    let autostart_manager = app.autolaunch();

    let current_state = match autostart_manager.is_enabled() {
        Ok(s) => s,
        Err(e) => {
            log::error!("Failed to get autostart state: {}", e);
            return;
        }
    };

    log::trace!(
        "Current autostart state: {}, Desired autostart state: {}",
        current_state,
        desired_state
    );

    if current_state != desired_state {
        if desired_state {
            match autostart_manager.enable() {
                Ok(_) => {
                    log::info!("Autostart enabled");
                }
                Err(e) => {
                    log::error!("Failed to enable autostart: {}", e);
                }
            }
        } else {
            match autostart_manager.disable() {
                Ok(_) => {
                    log::info!("Autostart disabled");
                }
                Err(e) => {
                    log::error!("Failed to disable autostart: {}", e);
                }
            }
        }

        // Update settings struct to reflect the new state
        if let Ok(mut settings) = settings.lock() {
            settings.start_app_with_system = desired_state;
        } else {
            log::error!("Failed to lock settings mutex");
        }
    }
}

/// Sync the settings autostart state with the actual system autostart state
pub fn sync_autostart_state(app: &tauri::AppHandle, settings: &mut Settings) {
    let autostart_manager = app.autolaunch();
    match autostart_manager.is_enabled() {
        Ok(state) => {
            settings.start_app_with_system = state;
            log::info!("Synced autostart state: {}", state);
        }
        Err(e) => {
            log::error!("Failed to get autostart state: {}", e);
        }
    }
}
