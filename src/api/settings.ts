import { invoke } from "@tauri-apps/api/core";
import { debug, error } from "@tauri-apps/plugin-log";
import type { Settings } from "../../src-tauri/bindings/Settings";

export async function getSettings(): Promise<Settings> {
  try {
    debug("[frontend] invoking get_settings");
    const result = await invoke<Settings>("get_settings");
    debug("[frontend] got settings from backend:" + result);
    return result;
  } catch (e) {
    error("[frontend] invoke(get_settings) failed:" + e);
    throw e;
  }
}

export async function updateSettings(newSettings: Settings): Promise<Settings> {
  return await invoke<Settings>("update_settings", { newSettings });
}

export async function resetSettings(): Promise<Settings> {
  return await invoke<Settings>("reset_settings");
}
