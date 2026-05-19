import { createSignal, onMount } from "solid-js";
import { error, trace } from "@tauri-apps/plugin-log";
import type { Settings } from "../../src-tauri/bindings/Settings";
import type { DiscordRichPresenceFields } from "../../src-tauri/bindings/DiscordRichPresenceFields";
import { getSettings, updateSettings, resetSettings } from "../api";

export type SettingsStatus = "loading" | "error" | "ready";

export function useSettings() {
  const [settings, setSettings] = createSignal<Settings | null>(null);
  const [status, setStatus] = createSignal<SettingsStatus>("loading");

  onMount(async () => {
    trace("Loading settings from backend…");
    try {
      const backendSettings = await getSettings();
      trace("Settings loaded from backend: " + JSON.stringify(backendSettings));
      setSettings(backendSettings);
      setStatus("ready");
      trace("App is ready.");
    } catch (err) {
      error("Failed to load settings from backend: " + String(err));
      setStatus("error");
    }
  });

  const reload = async () => {
    setStatus("loading");
    try {
      const backendSettings = await getSettings();
      setSettings(backendSettings);
      setStatus("ready");
    } catch (err) {
      error("Failed to reload settings from backend: " + String(err));
      setStatus("error");
    }
  };

  // Safe accessor, only used when status() === "ready"
  const s = () => settings() as Settings;

  // Shared helper to update settings locally + backend
  const applyUpdate = (updater: (prev: Settings) => Settings) => {
    const current = settings();
    if (!current) return;

    const next = updater(current);
    // Optimistic update
    setSettings(next);
    trace("Applying settings update: " + JSON.stringify(next));

    void updateSettings(next)
      .then((serverSettings) => {
        trace(
          "Backend returned normalized settings: " +
          JSON.stringify(serverSettings),
        );
        setSettings(serverSettings);
      })
      .catch((err) => {
        error("Failed to update settings in backend: " + String(err));
        // Revert local change on error
        setSettings(current);
      });
  };

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    applyUpdate((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const updateDiscordField = (
    key: keyof DiscordRichPresenceFields,
    value: boolean,
  ) => {
    applyUpdate((prev) => ({
      ...prev,
      discord_fields: {
        ...prev.discord_fields,
        [key]: value,
      },
    }));
  };

  const reset = async () => {
    try {
      const newSettings = await resetSettings();
      setSettings(newSettings);
    } catch (err) {
      error("Failed to reset settings: " + String(err));
    }
  };

  return {
    settings,
    status,
    s,
    reload,
    updateSetting,
    updateDiscordField,
    reset,
  };
}
