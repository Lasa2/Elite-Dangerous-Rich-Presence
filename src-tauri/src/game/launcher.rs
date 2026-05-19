use tauri_plugin_opener::OpenerExt;

use crate::settings::{ExecutablePath, LaunchMethod};

pub fn launch_elite_dangerous(
    app: &tauri::AppHandle,
    launch_via: &LaunchMethod,
    executable_path: &ExecutablePath,
    launch_arguments: &str,
) {
    log::debug!("Launching Elite Dangerous from launcher module");

    match launch_via {
        LaunchMethod::Steam | LaunchMethod::EpicGames => {
            let url = executable_path.url_scheme();
            if url.is_none() {
                log::error!(
                    "No URL scheme found for launch method {:?} and executable path {:?}",
                    launch_via,
                    executable_path
                );
                return;
            }
            if let Err(e) = app.opener().open_url(&url.unwrap(), None::<&str>) {
                log::error!("Failed to launch Elite Dangerous via Steam URL: {}", e);
            }
        }
        LaunchMethod::Executable => {
            let exec_path = match executable_path {
                ExecutablePath::None => {
                    log::error!("No executable path set for launching Elite Dangerous");
                    return;
                }
                ExecutablePath::Steam | ExecutablePath::EpicGames => {
                    log::error!(
                        "Executable path is set to {:?} but launch method is Executable",
                        executable_path
                    );
                    return;
                }
                ExecutablePath::Custom(path) => path,
            };

            let args: Vec<&str> = if launch_arguments.is_empty() {
                vec![]
            } else {
                launch_arguments.split_whitespace().collect()
            };

            match std::process::Command::new(exec_path).args(&args).spawn() {
                Ok(_child) => {
                    log::debug!(
                        "Successfully launched Elite Dangerous executable: {:?} with args: {:?}",
                        exec_path,
                        args
                    );
                }
                Err(e) => {
                    log::error!(
                        "Failed to launch Elite Dangerous executable: {:?} with args: {:?}: {}",
                        exec_path,
                        args,
                        e
                    );
                }
            }
        }
    }
}
