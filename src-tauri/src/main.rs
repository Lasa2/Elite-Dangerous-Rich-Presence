#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod log;
mod settings;
mod util;

static IDENTIFIER: &str = "icu.veelume.elite-dangerous-rich-presence";

use once_cell::sync::OnceCell;
use std::{
    path::PathBuf,
    sync::{
        RwLock,
        atomic::{AtomicBool, Ordering},
    },
};
use tracing::{error, info};
use tracing_appender::{
    non_blocking::WorkerGuard,
    rolling::{RollingFileAppender, Rotation},
};
use tracing_subscriber::{filter::EnvFilter, fmt, prelude::*, reload};

use tauri::{
    Manager, State, WebviewUrl, WebviewWindowBuilder, Wry,
    image::Image,
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
};
use tauri_plugin_autostart::MacosLauncher;

use crate::{
    log::{init_tracing, update_log_filter},
    settings::Settings,
};

#[derive(Default)]
struct ExitState {
    pub allow_exit: AtomicBool,
}

#[derive(Default)]
struct SettingsState {
    inner: RwLock<Settings>,
}

fn do_launch_game(settings: &Settings) -> Result<(), String> {
    println!("Launching game with method: {:?}", settings.launch_method);
    // TODO: your real launcher logic here
    Ok(())
}

// ───────────── Tauri commands callable from SolidJS ─────────────

#[tauri::command]
fn cmd_load_settings(state: State<'_, SettingsState>) -> Settings {
    state.inner.read().unwrap().clone()
}

#[tauri::command]
fn cmd_update_settings(new_settings: Settings, state: State<'_, SettingsState>) -> Result<(), ()> {
    {
        let mut guard = state.inner.write().unwrap();
        *guard = new_settings.clone();
    }

    // Update log filter at runtime when log_level changes
    update_log_filter(&new_settings);

    new_settings.save_to_disk()
}

#[tauri::command]
fn cmd_launch_game(state: State<'_, SettingsState>) -> Result<(), String> {
    let settings = state.inner.read().unwrap().clone();
    do_launch_game(&settings)
}

#[tauri::command]
fn cmd_show_main_window(window: tauri::Window) {
    window.get_webview_window("main").unwrap().show().unwrap();
}

#[tauri::command]
fn cmd_reset_settings(state: State<'_, SettingsState>) -> Result<Settings, ()> {
    let default_settings = Settings::default();
    {
        let mut guard = state.inner.write().unwrap();
        *guard = default_settings.clone();
    }

    // Update log filter at runtime when log_level changes
    update_log_filter(&default_settings);

    default_settings.save_to_disk()?;
    Ok(default_settings)
}

// ───────────── main ─────────────

fn main() {
    // 1. Load settings first so we can configure logging
    let initial_settings = Settings::load_from_disk();

    // 2. Initialize tracing based on settings.log_level
    init_tracing(&initial_settings);

    // 3. Build Tauri and inject states
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_autostart::init(
            MacosLauncher::LaunchAgent,
            None,
        ))
        .manage(ExitState::default())
        .manage(SettingsState {
            inner: RwLock::new(initial_settings),
        })
        .invoke_handler(tauri::generate_handler![
            cmd_load_settings,
            cmd_update_settings,
            cmd_launch_game,
            cmd_show_main_window,
            cmd_reset_settings,
        ])
        .setup(|app| {
            use tauri::menu::{Menu, MenuItem};
            use tauri::tray::TrayIconBuilder;

            // Create menu items
            let settings_i = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>)?;
            let launch_i =
                MenuItem::with_id(app, "launch_game", "Launch Game", true, None::<&str>)?;
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;

            // Attach the items to a menu
            let menu = Menu::with_items(app, &[&settings_i, &launch_i, &quit_i])?;

            let webview_url = WebviewUrl::App("index.html".into());

            // Create tray icon with that menu and an on_menu_event handler
            TrayIconBuilder::new()
                .icon(
                    Image::from_bytes(include_bytes!("../icons/elite-dangerous-clean.ico"))
                        .expect("Failed to load tray icon"),
                )
                .menu(&menu)
                .on_menu_event(move |app, event| {
                    match event.id.as_ref() {
                        "settings" => {
                            let label = "main";

                            if let Some(window) = app.get_webview_window(label) {
                                let _ = window.unminimize();
                                let _ = window.show();
                                let _ = window.set_focus();
                            } else {
                                // Create the settings window lazily
                                if let Ok(window) =
                                    WebviewWindowBuilder::new(app, label, webview_url.clone())
                                        .title("Elite Dangerous Rich Presence Settings")
                                        .resizable(true)
                                        .decorations(false)
                                        .visible(false)
                                        .inner_size(1000.0, 700.0)
                                        .build()
                                {
                                    let _ = window.set_focus();
                                }
                            }
                        }
                        "launch_game" => {
                            if let Some(settings_state) = app.try_state::<SettingsState>() {
                                let settings = settings_state.inner.read().unwrap().clone();
                                if let Err(err) = do_launch_game(&settings) {
                                    error!("Failed to launch game: {err}");
                                }
                            } else {
                                error!("SettingsState not available");
                            }
                        }
                        "quit" => {
                            if let Some(exit_state) = app.try_state::<ExitState>() {
                                exit_state.allow_exit.store(true, Ordering::Relaxed);
                            }
                            app.exit(0);
                        }
                        _ => {}
                    }
                })
                .build(app)?;

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while running tauri application")
        .run(|app, event: tauri::RunEvent| match event {
            tauri::RunEvent::ExitRequested { api, .. } => {
                let allow_exit = app
                    .try_state::<ExitState>()
                    .map(|state| state.allow_exit.load(Ordering::Relaxed))
                    .unwrap_or(false);

                if !allow_exit {
                    api.prevent_exit();
                }
            }
            _ => {}
        });
}
