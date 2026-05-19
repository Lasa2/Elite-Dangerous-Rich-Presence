use crate::game::detection::GameStatus;
use crate::game::service::SharedGameService;

#[tauri::command]
pub fn get_game_status(service: tauri::State<SharedGameService>) -> GameStatus {
    log::trace!("Getting game status");
    let status = service.status();
    log::debug!("Game status: {:?}", status);
    status
}
