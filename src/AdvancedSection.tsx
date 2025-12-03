import { For, type JSX } from "solid-js";
import type { LogLevel } from "../src-tauri/bindings/LogLevel";
import type { Settings } from "../src-tauri/bindings/Settings";

interface AdvancedSectionProps {
    settings: Settings;
    logLevels: LogLevel[];
    onUpdateSetting: <K extends keyof Settings>(
        key: K,
        value: Settings[K]
    ) => void;
    onReset: () => void;
    onBrowseGameDirectory: () => void;
}

export function AdvancedSection(props: AdvancedSectionProps): JSX.Element {
    const s = () => props.settings;

    return (
        <section class="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-4">
            <div class="flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-sm font-semibold text-slate-100">Advanced</h2>
                    <p class="text-xs text-slate-400 mt-1">
                        Paths, logging and maintenance options. You usually don&apos;t need to
                        touch these.
                    </p>
                </div>
            </div>

            <div class="flex items-center gap-3">
                <span class="w-32 text-xs text-slate-400 tracking-wide">
                    Game directory
                </span>
                <input
                    class="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-2 py-1 text-xs placeholder:text-slate-500"
                    readonly
                    value={s().game_directory ?? ""}
                    placeholder="Select your Elite Dangerous game folder"
                />
                <button
                    class="px-3 py-1 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-xs"
                    onClick={props.onBrowseGameDirectory}
                >
                    Browse
                </button>
            </div>

            <div class="flex items-center gap-3">
                <span class="w-32 text-xs text-slate-400 tracking-wide">Log level</span>
                <select
                    class="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-2 py-1 text-xs"
                    value={s().log_level}
                    onInput={(e) =>
                        props.onUpdateSetting("log_level", e.currentTarget.value as LogLevel)
                    }
                >
                    <For each={props.logLevels}>
                        {(lvl) => <option value={lvl}>{lvl}</option>}
                    </For>
                </select>
            </div>

            <div class="pt-2 flex justify-end">
                <button
                    class="px-3 py-1.5 rounded-lg border border-red-500/70 text-xs text-red-300 hover:bg-red-500/10"
                    onClick={props.onReset}
                >
                    Reset settings to defaults
                </button>
            </div>
        </section>
    );
}
