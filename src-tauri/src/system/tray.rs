use tauri::menu::{Menu, MenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::{include_image, Manager, WebviewUrl, WebviewWindowBuilder};

pub fn create_tray(app: &tauri::App) -> tauri::Result<()> {
    let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let launch_i = MenuItem::with_id(app, "launch", "Launch Elite Dangerous", true, None::<&str>)?;
    let settings_i = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>)?;

    let menu = Menu::with_items(app, &[&launch_i, &settings_i, &quit_i])?;

    let webview_url = WebviewUrl::App("index.html".into());
    let image = include_image!("../assets/elite-dangerous-minimalistic.png");

    // Build tray icon
    let tray_builder = TrayIconBuilder::new()
        .title("Elite Dangerous Rich Presence")
        .icon(image)
        .menu(&menu)
        .on_menu_event(move |app, event| match event.id.as_ref() {
            "quit" => {
                app.exit(1);
            }
            "launch" => {
                log::debug!("Launching Elite Dangerous from tray menu");
            }
            "settings" => {
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
                    return;
                }

                match WebviewWindowBuilder::new(app, "settings", webview_url.clone())
                    .title("Settings")
                    .resizable(true)
                    .decorations(false)
                    .inner_size(800., 720.)
                    .center()
                    .focused(true)
                    .visible(false)
                    .build()
                {
                    Ok(window) => {
                        if let Err(e) = window.show() {
                            log::error!("Failed to show settings window: {}", e);
                        }
                    }
                    Err(e) => {
                        log::error!("Failed to build settings window: {}", e);
                    }
                }
            }
            _ => {}
        });

    if let Err(e) = tray_builder.build(app) {
        log::error!("Failed to build tray icon: {}", e);
    }

    Ok(())
}
