import type { Settings } from "../../../src-tauri/bindings/Settings";
import { SectionHeader, Toggle } from "../ui";

type GeneralSectionProps = {
  settings: Settings;
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
};

export function GeneralSection(props: GeneralSectionProps) {
  return (
    <section class="bg-zinc-900/80 border border-zinc-700/40 rounded-lg p-2 shadow-[0_0_12px_rgba(249,115,22,0.04)]">
      <SectionHeader
        title="General"
        description="Overall behavior of the companion app."
      />

      <div class="grid grid-cols-1 md:grid-cols-2 gap-1.5">
        <Toggle
          label="Start with Windows"
          description="Launch this app automatically when your PC starts."
          checked={props.settings.start_app_with_system}
          onChange={(val) => props.updateSetting("start_app_with_system", val)}
        />
        <Toggle
          label="Start minimized to tray"
          description="Keep the window hidden and only show a tray icon on startup."
          checked={props.settings.start_to_tray}
          onChange={(val) => props.updateSetting("start_to_tray", val)}
        />
        <Toggle
          label="Close app when game closes"
          description="Automatically exit this app when Elite Dangerous is no longer running."
          checked={props.settings.close_with_game}
          onChange={(val) => props.updateSetting("close_with_game", val)}
        />
        <Toggle
          label="Check for app updates"
          description="Periodically check for new versions of this companion app."
          checked={props.settings.check_for_updates}
          onChange={(val) => props.updateSetting("check_for_updates", val)}
        />
      </div>
    </section>
  );
}
