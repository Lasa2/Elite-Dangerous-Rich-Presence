use std::path::PathBuf;

use crate::IDENTIFIER;

pub fn get_data_dir() -> PathBuf {
    let data_dir = dirs::data_dir().unwrap_or_else(|| PathBuf::from("."));
    data_dir.join(IDENTIFIER)
}
