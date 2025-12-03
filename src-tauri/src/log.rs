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

use crate::{settings::Settings, util::get_data_dir};

const LOG_TARGET: &str = "elite_dangerous_rich_presence";
static LOG_GUARD: OnceCell<WorkerGuard> = OnceCell::new();
static FILTER_HANDLE: OnceCell<reload::Handle<EnvFilter, tracing_subscriber::registry::Registry>> =
    OnceCell::new();

fn make_filter(settings: &Settings) -> EnvFilter {
    let level_str = settings.log_level.as_filter_str();

    // Example result: "elite_dangerous_rich_presence=debug,info"
    // meaning:
    //   - your crate: debug (from settings)
    //   - everything else: info
    let spec = format!(
        "{crate}={level},info",
        crate = LOG_TARGET,
        level = level_str
    );

    EnvFilter::new(spec)
}

pub fn init_tracing(settings: &Settings) {
    use std::fs;

    let log_dir = get_data_dir();

    if let Err(e) = fs::create_dir_all(&log_dir) {
        eprintln!("Failed to create log dir {:?}: {}", log_dir, e);
        // we'll still try to continue, but file logging may be broken
    }

    // A single file (no rotation). Swap to rolling::daily(...) if you want.
    let rolling_appender = RollingFileAppender::builder()
        .rotation(Rotation::DAILY) // one file per day
        .filename_prefix("ed_rich_presence.log") // files like ed_rich_presence.log.2025-12-02
        .max_log_files(31) // keep about the last 31 days of logs
        .build(&log_dir)
        .expect("failed to initialize rolling file appender");
    let (non_blocking, guard) = tracing_appender::non_blocking(rolling_appender);

    // Keep the guard alive so logging thread doesn't shut down
    let _ = LOG_GUARD.set(guard);

    let level_str = settings.log_level.as_filter_str();

    // Build initial filter
    let filter = make_filter(settings);

    let (filter_layer, handle) =
        reload::Layer::<EnvFilter, tracing_subscriber::registry::Registry>::new(filter);

    // Store handle so we can change level at runtime
    let _ = FILTER_HANDLE.set(handle);

    // Build subscriber: registry + reloadable filter + fmt layer to file
    let subscriber = tracing_subscriber::registry().with(filter_layer).with(
        fmt::layer().with_writer(non_blocking).with_ansi(false), // file logs: no colors
    );

    if let Err(e) = tracing::subscriber::set_global_default(subscriber) {
        eprintln!("Failed to set global tracing subscriber: {}", e);
    } else {
        info!("Tracing initialized with level {}", level_str);
    }
}

// Called whenever settings change
pub fn update_log_filter(settings: &Settings) {
    if let Some(handle) = FILTER_HANDLE.get() {
        let level_str = settings.log_level.as_filter_str();
        let filter = make_filter(settings);

        if let Err(e) = handle.modify(|f| *f = filter) {
            eprintln!("Failed to update log filter: {}", e);
        } else {
            info!("Updated log level to {}", level_str);
        }
    } else {
        eprintln!("FILTER_HANDLE not initialized; cannot update log filter");
    }
}
