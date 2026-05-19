import { Show } from "solid-js";
import "./App.css";
import { Titlebar } from "./components/Titlebar";
import {
  AdvancedSection,
  DiscordSection,
  GeneralSection,
  LaunchSection,
} from "./components/sections";
import { useSettings } from "./hooks";

function App() {
  const {
    status,
    s,
    reload,
    updateSetting,
    updateDiscordField,
    reset,
  } = useSettings();

  return (
    <div class="h-screen flex flex-col bg-gradient-to-br from-black via-[#050816] to-black text-zinc-100">
      <Titlebar />

      <Show when={status() === "loading"}>
        <main class="flex-1 flex items-center justify-center text-xs text-zinc-400">
          Loading settings…
        </main>
      </Show>

      <Show when={status() === "error"}>
        <main class="flex-1 flex flex-col items-center justify-center text-xs text-zinc-300 gap-2">
          <div>Failed to load settings from backend.</div>
          <button
            type="button"
            class="h-7 px-3 rounded-md border border-orange-500/60 text-[11px] text-orange-100 bg-zinc-900/80 hover:bg-orange-500/80 hover:text-black transition"
            onClick={reload}
          >
            Retry
          </button>
        </main>
      </Show>

      <Show when={status() === "ready"}>
        <main class="flex-1 overflow-auto px-1 py-1">
          <div class="space-y-2">
            <GeneralSection
              settings={s()}
              updateSetting={updateSetting}
            />

            <DiscordSection
              discordFields={s().discord_fields}
              updateDiscordField={updateDiscordField}
            />

            <LaunchSection
              settings={s()}
              updateSetting={updateSetting}
            />

            <AdvancedSection
              settings={s()}
              updateSetting={updateSetting}
              onReset={reset}
            />
          </div>
        </main>
      </Show>
    </div>
  );
}

export default App;
