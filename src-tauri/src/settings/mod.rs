mod defaults;
mod models;
mod persistence;
mod validation;

pub use models::{DiscordRichPresenceFields, ExecutablePath, LaunchMethod, LogLevel, Settings};

#[cfg(test)]
mod ts_export {
    use super::*;

    #[test]
    fn export_ts() {
        // The derives + #[ts(export,...)] are enough; referencing the types
        // here ensures the codegen runs.
        let _ = LogLevel::Info;
        let _ = LaunchMethod::Steam;
        let _ = ExecutablePath::None;
        let _ = Settings::default();
        let _ = DiscordRichPresenceFields::default();
    }
}
