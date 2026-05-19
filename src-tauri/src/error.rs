use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("Failed to lock settings mutex")]
    SettingsLock,

    #[error("Invalid game directory: {0}")]
    InvalidGameDirectory(String),

    #[error("Invalid executable path: {0}")]
    InvalidExecutablePath(String),

    #[error("Failed to save settings: {0}")]
    SettingsSave(String),

    #[error("Failed to load settings: {0}")]
    SettingsLoad(String),

    #[error("Launch error: {0}")]
    LaunchError(String),

    #[error("Autostart error: {0}")]
    AutostartError(String),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

pub type AppResult<T> = Result<T, AppError>;
