import { open } from "@tauri-apps/plugin-dialog";
import type { Settings } from "../../../src-tauri/bindings/Settings";
import type { LogLevel } from "../../../src-tauri/bindings/LogLevel";
import { Button, SectionHeader } from "../ui";

type AdvancedSectionProps = {
  settings: Settings;
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
  onReset: () => void;
};

export function AdvancedSection(props: AdvancedSectionProps) {
  const handlePickGameDirectory = async () => {
    const selectedDir = (await open({
      multiple: false,
      directory: true,
      title: "Select Elite Dangerous Game Directory",
    })) as string | null;

    if (!selectedDir) return;
    props.updateSetting("game_directory", selectedDir);
  };

  return (
    <section class="bg-zinc-900/80 border border-zinc-700/40 rounded-lg p-2 shadow-[0_0_12px_rgba(249,115,22,0.04)] mb-1">
      <SectionHeader
        title="Advanced"
        description="Paths, logging and maintenance."
        rightElement={
          <Button variant="danger" size="sm" onClick={props.onReset}>
            Reset
          </Button>
        }
      />

      <div class="space-y-2">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 items-start">
          {/* Game directory */}
          <div class="space-y-1">
            <label class="text-[11px] font-medium text-zinc-300">
              Game directory
            </label>
            <div class="flex items-center gap-2">
              <input
                type="text"
                readOnly
                class="flex-1 h-8 bg-zinc-900/70 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none select-text"
                value={props.settings.game_directory ?? ""}
              />
              <Button onClick={handlePickGameDirectory}>
                Select
              </Button>
            </div>
            <p class="text-[10px] text-zinc-500">Journal files location.</p>
          </div>

          {/* Log level */}
          <div class="space-y-1">
            <label class="text-[11px] font-medium text-zinc-300">
              Log level
            </label>
            <select
              class="ed-select w-full h-8 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-orange-400 focus:border-orange-400"
              value={props.settings.log_level}
              onChange={(e) =>
                props.updateSetting("log_level", e.currentTarget.value as LogLevel)
              }
            >
              <option value="Trace">Trace</option>
              <option value="Debug">Debug</option>
              <option value="Info">Info</option>
              <option value="Warn">Warn</option>
              <option value="Error">Error</option>
            </select>
            <p class="text-[10px] text-zinc-500">Controls log verbosity.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
