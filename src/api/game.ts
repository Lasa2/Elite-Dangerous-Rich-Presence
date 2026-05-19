import { invoke } from "@tauri-apps/api/core";
import type { GameStatus } from "../../src-tauri/bindings/GameStatus";

export async function launchGame(): Promise<void> {
  await invoke("launch_game");
}

export async function getGameStatus(): Promise<GameStatus> {
  return await invoke<GameStatus>("get_game_status");
}
