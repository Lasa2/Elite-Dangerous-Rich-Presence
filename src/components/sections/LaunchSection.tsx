import { open } from "@tauri-apps/plugin-dialog";
import { error } from "@tauri-apps/plugin-log";
import type { Settings } from "../../../src-tauri/bindings/Settings";
import type { ExecutablePath } from "../../../src-tauri/bindings/ExecutablePath";
import type { LaunchMethod } from "../../../src-tauri/bindings/LaunchMethod";
import { launchGame } from "../../api";
import { Button, SectionHeader, Toggle } from "../ui";

const steamURL = "steam://launch/359320";
const epicGamesURL =
  "com.epicgames.launcher://apps/3db17abfd650423f993291624b1b2ac1%3A9b8ee44da2e84b139c7444ab002cbc35%3A9c203b6ed35846e8a4a9ff1e314f6593?action=launch&silent=true";

const executablePathToDisplay = (path: ExecutablePath): string => {
  if (path === "Steam") return steamURL;
  if (path === "EpicGames") return epicGamesURL;
  if (path === "None") return "";
  if (typeof path === "object" && "Custom" in path) return path.Custom;
  return "";
};

type LaunchSectionProps = {
  settings: Settings;
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
};

export function LaunchSection(props: LaunchSectionProps) {
  const handlePickExecutablePath = async () => {
    const selectedPath = (await open({
      multiple: false,
      directory: false,
      title: "Select Elite Dangerous Executable",
      filters: [
        {
          name: "Executable",
          extensions: ["exe", "bin", "app"],
        },
      ],
    })) as string | null;

    if (!selectedPath) return;
    props.updateSetting("executable_path", { Custom: selectedPath });
  };

  const handleLaunchGame = async () => {
    try {
      await launchGame();
    } catch (err) {
      error("Failed to launch game: " + String(err));
    }
  };

  return (
    <section class="bg-zinc-900/80 border border-zinc-700/40 rounded-lg p-2 shadow-[0_0_12px_rgba(249,115,22,0.04)]">
      <SectionHeader
        title="Launch Options"
        description="Configure how the game is started."
        rightElement={
          <Button variant="primary" size="sm" onClick={handleLaunchGame}>
            Launch game
          </Button>
        }
      />

      <div class="space-y-2">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div class="space-y-1">
            <label class="text-[11px] leading-none font-medium text-zinc-300">
              Launch via
            </label>
            <select
              class="ed-select w-full h-8 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-orange-400 focus:border-orange-400"
              value={props.settings.launch_method}
              onChange={(e) =>
                props.updateSetting("launch_method", e.currentTarget.value as LaunchMethod)
              }
            >
              <option value="Steam">Steam</option>
              <option value="EpicGames">Epic Games</option>
              <option value="Executable">Executable</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-[11px] leading-none font-medium text-zinc-300">
              Launch arguments
            </label>
            <input
              type="text"
              class="w-full h-8 bg-zinc-900/70 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-orange-400 focus:border-orange-400 disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Optional"
              value={props.settings.launch_method !== "Executable" ? "" : props.settings.launch_arguments}
              disabled={props.settings.launch_method !== "Executable"}
              onInput={(e) =>
                props.updateSetting("launch_arguments", e.currentTarget.value)
              }
            />
          </div>
        </div>

        {/* Executable path */}
        <div class="space-y-1">
          <div class="flex items-center justify-between text-[11px]">
            <span class="font-medium text-zinc-300">Executable path</span>
            <span class="text-[10px] text-zinc-500">
              Only used with "Executable"
            </span>
          </div>
          <div class="flex items-center gap-2">
            <input
              type="text"
              readOnly
              class="flex-1 h-8 bg-zinc-900/70 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none select-text"
              value={executablePathToDisplay(props.settings.executable_path)}
            />
            <Button
              disabled={props.settings.launch_method !== "Executable"}
              onClick={handlePickExecutablePath}
            >
              Select file
            </Button>
          </div>
        </div>

        <Toggle
          label="Auto start game with this app"
          description="Start Elite Dangerous automatically when this app launches."
          checked={props.settings.start_game_with_app}
          onChange={(val) => props.updateSetting("start_game_with_app", val)}
        />
      </div>
    </section>
  );
}
