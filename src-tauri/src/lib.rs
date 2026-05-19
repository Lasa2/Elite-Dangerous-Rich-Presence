mod commands;
mod error;
mod game;
mod settings;
mod system;

use std::sync::Mutex;

use tauri::Manager;

use crate::commands::{get_game_status, get_settings, launch_game, reset_settings, update_settings};
use crate::game::service::create_service;
use crate::settings::Settings;
use crate::system::{autostart::sync_autostart_state, tray::create_tray};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_settings,
            update_settings,
            reset_settings,
            launch_game,
            get_game_status
        ])
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
            log::info!("Another instance attempted to start.");
            log::debug!("Arguments: {:?}, CWD: {:?}", argv, cwd);
            if let Some(window) = app.get_webview_window("settings") {
                if let Err(e) = window.unminimize() {
                    log::error!("Failed to unminimize settings window: {}", e);
                }
                if let Err(e) = window.show() {
                    log::error!("Failed to show settings window: {}", e);
                }
                if let Err(e) = window.set_focus() {
                    log::error!("Failed to focus settings window: {}", e);
                }
            }
        }))
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(
            tauri_plugin_log::Builder::new()
                .rotation_strategy(tauri_plugin_log::RotationStrategy::KeepSome(14))
                .level(log::LevelFilter::Trace)
                .build(),
        )
        .plugin(tauri_plugin_opener::init())
        .setup(|app: &mut tauri::App| {
            let mut settings = Settings::load_from_disk(app.handle());
            log::info!("Loaded settings: {:?}", settings);

            // Sync autostart state with system
            sync_autostart_state(app.handle(), &mut settings);

            // Apply log level from settings
            log::set_max_level(settings.log_level.clone().into());

            app.manage(Mutex::new(settings));

            // Initialize and start the game service
            let game_service = create_service(app.handle());
            app.manage(game_service);

            if let Err(e) = create_tray(&app) {
                log::error!("Failed to create tray: {}", e);
            }
            Ok(())
        });

    match builder.build(tauri::generate_context!()) {
        Ok(app) => app.run(|_app, event| match event {
            tauri::RunEvent::ExitRequested { api, code, .. } => {
                log::debug!("Exit requested with code: {:?}", code);
                if code == None {
                    api.prevent_exit();
                }
            }
            _ => {}
        }),
        Err(e) => {
            log::error!("Error while building tauri application: {}", e);
        }
    }
}
