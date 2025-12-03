import { invoke } from "@tauri-apps/api/core";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import {
  disable as disableAutostart,
  enable as enableAutostart,
  isEnabled as isAutostartEnabled,
} from "@tauri-apps/plugin-autostart";
import { createEffect, createSignal, onMount, Show } from "solid-js";
import type { LogLevel } from "../src-tauri//bindings/LogLevel";
import type { Settings } from "../src-tauri//bindings/Settings";
import type { DiscordRichPresenceFields } from "../src-tauri/bindings/DiscordRichPresenceFields";
import type { LaunchMethod } from "../src-tauri/bindings/LaunchMethod";
import { AdvancedSection } from "./AdvancedSection";
import { DiscordSection } from "./DiscordSection";
import { GeneralSection } from "./GeneralSection";
import { LaunchOptionsSection } from "./LaunchOptionsSection";
import { Titlebar } from "./Titlebar";
import { open } from "@tauri-apps/plugin-dialog";



async function loadSettings(): Promise<Settings> {
  return await invoke<Settings>("cmd_load_settings");
}

async function updateSettings(settings: Settings): Promise<void> {
  await invoke("cmd_update_settings", { newSettings: settings });
}

async function launchGame(): Promise<void> {
  await invoke("cmd_launch_game");
}

export default function App() {
  const [settings, setSettings] = createSignal<Settings | null>(null);
  const [saving, setSaving] = createSignal(false);
  const [loading, setLoading] = createSignal(true);
  const [isMaximized, setIsMaximized] = createSignal(false);

  const logLevels: LogLevel[] = ["Trace", "Debug", "Info", "Warn", "Error"];
  const launchMethodLabels: Record<LaunchMethod, string> = {
    Steam: "Steam",
    EpicGames: "Epic Games",
    Executable: "Executable",
  };
  const currentWindow = getCurrentWebviewWindow();

  const handleMinimize = () => {
    currentWindow.minimize();
  };

  const handleToggleMaximize = async () => {
    await currentWindow.toggleMaximize();
    const max = await currentWindow.isMaximized();
    setIsMaximized(max);
  };

  const handleHeaderDoubleClick = async () => {
    await currentWindow.toggleMaximize();
    const max = await currentWindow.isMaximized();
    setIsMaximized(max);
  };

  const handleClose = () => {
    currentWindow.close();
  };

  const handleHeaderMouseDown = (e: MouseEvent) => {
    if (e.button !== 0) return;
    if (e.detail === 2) return; // let dblclick do maximize/restore
    currentWindow.startDragging();
  };

  // Load settings once on mount
  onMount(async () => {
    const loaded = await loadSettings();
    setSettings(loaded);
    setLoading(false);

    // sync from OS autostart state -> settings flag
    try {
      const enabled = await isAutostartEnabled();
      setSettings((current) =>
        current ? { ...current, launch_on_system_startup: enabled } : current
      );
    } catch (err) {
      console.error("Failed to read autostart state", err);
    }

    const max = await currentWindow.isMaximized();
    setIsMaximized(max);

    invoke("cmd_show_main_window");
  });

  // Debounced auto-save
  let saveTimeout: number | undefined;
  createEffect(() => {
    const s = settings();
    if (!s) return;

    if (saveTimeout !== undefined) {
      clearTimeout(saveTimeout);
    }

    saveTimeout = window.setTimeout(async () => {
      setSaving(true);
      try {
        await updateSettings(s);
      } catch (err) {
        console.error("Failed to save settings", err);
      } finally {
        setSaving(false);
      }
    }, 300);
  });

  const update = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings((current) => {
      if (!current) return current;
      return { ...current, [key]: value };
    });
  };

  const updateDiscord = <K extends keyof DiscordRichPresenceFields>(
    key: K,
    value: DiscordRichPresenceFields[K]
  ) => {
    setSettings((current) => {
      if (!current) return current;
      const discord = { ...current.discord_fields, [key]: value };
      return { ...current, discord_fields: discord };
    });
  };

  const onLaunch = async () => {
    await launchGame();
  };

  const onResetSettings = async () => {
    try {
      // Assumes you have a Tauri command that resets to defaults and returns them.
      const defaults = await invoke<Settings>("cmd_reset_settings");
      setSettings(defaults);
    } catch (err) {
      console.error("Failed to reset settings", err);
    }
  };

  const pickGameDirectory = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
      });

      // open() can return string | string[] | null
      if (!selected || Array.isArray(selected)) return;

      update("game_directory", selected);
    } catch (err) {
      console.error("Failed to pick game directory", err);
    }
  };

  const pickExecutable = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: "Executable",
            extensions: ["exe"], // tweak if you need other platforms
          },
        ],
      });

      if (!selected || Array.isArray(selected)) return;

      update("executable_path", selected);
    } catch (err) {
      console.error("Failed to pick executable", err);
    }
  };



  const setLaunchOnStartup = async (enabled: boolean) => {
    // persist to your settings (and trigger auto-save)
    update("launch_on_system_startup", enabled);

    // actually enable/disable OS autostart
    try {
      if (enabled) {
        await enableAutostart();
      } else {
        await disableAutostart();
      }
    } catch (err) {
      console.error("Failed to update autostart", err);
    }
  };

  return (
    <div class="min-h-screen bg-slate-900 text-slate-100">
      <div class="h-full flex flex-col">
        <Titlebar
          isMaximized={isMaximized()}
          onMinimize={handleMinimize}
          onToggleMaximize={handleToggleMaximize}
          onClose={handleClose}
          onHeaderMouseDown={handleHeaderMouseDown}
          onHeaderDoubleClick={handleHeaderDoubleClick}
        />

        <main class="flex-1 overflow-auto px-8 py-6">
          <div class="space-y-6">
            <p class="text-sm text-slate-400">
              Configure how this companion app behaves, how your status appears
              on Discord, and how the game is launched.
            </p>

            <Show
              when={!loading()}
              fallback={<p class="text-slate-400">Loading settings…</p>}
            >
              <Show
                when={settings()}
                fallback={<p class="text-red-400">Failed to load settings.</p>}
              >
                {(s) => (
                  <div class="space-y-5 text-sm">
                    <GeneralSection
                      settings={s()}
                      onUpdateSetting={update}
                      onSetLaunchOnStartup={setLaunchOnStartup}
                    />

                    <DiscordSection
                      discord={s().discord_fields}
                      onUpdateDiscord={updateDiscord}
                    />

                    <LaunchOptionsSection
                      settings={s()}
                      launchMethodLabels={launchMethodLabels}
                      onUpdateSetting={update}
                      onLaunch={onLaunch}
                      onBrowseExecutable={pickExecutable}
                    />


                    <AdvancedSection
                      settings={s()}
                      logLevels={logLevels}
                      onUpdateSetting={update}
                      onReset={onResetSettings}
                      onBrowseGameDirectory={pickGameDirectory}
                    />
                  </div>

                )}
              </Show>
            </Show>
          </div>
        </main>
      </div>
    </div>
  );
}
