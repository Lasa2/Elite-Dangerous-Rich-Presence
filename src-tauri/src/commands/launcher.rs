use std::sync::Mutex;

use crate::error::{AppError, AppResult};
use crate::game::launcher;
use crate::settings::Settings;

#[tauri::command]
pub fn launch_game(
    app: tauri::AppHandle,
    settings: tauri::State<Mutex<Settings>>,
) -> AppResult<()> {
    log::trace!("Launching game from backend");
    let settings = settings.lock().map_err(|_| AppError::SettingsLock)?.clone();
    log::debug!("Launching game with settings: {:?}", settings);

    launcher::launch_elite_dangerous(
        &app,
        &settings.launch_method,
        &settings.executable_path,
        &settings.launch_arguments,
    );
    Ok(())
}
