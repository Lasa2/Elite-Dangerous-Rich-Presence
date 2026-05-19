use super::models::{ExecutablePath, Settings};

impl Settings {
    pub fn validate_game_directory(&self) -> bool {
        if let Some(ref path) = self.game_directory {
            path.exists() && path.is_dir()
        } else {
            false
        }
    }

    pub fn validate_executable_path(&self) -> bool {
        match &self.executable_path {
            ExecutablePath::Custom(path) => path.exists() && path.is_file(),
            ExecutablePath::Steam | ExecutablePath::EpicGames => true,
            ExecutablePath::None => false,
        }
    }
}
