import { For, Show, type JSX } from "solid-js";
import type { LaunchMethod } from "../src-tauri/bindings/LaunchMethod";
import type { Settings } from "../src-tauri/bindings/Settings";

interface LaunchOptionsSectionProps {
    settings: Settings;
    launchMethodLabels: Record<LaunchMethod, string>;
    onUpdateSetting: <K extends keyof Settings>(
        key: K,
        value: Settings[K]
    ) => void;
    onLaunch: () => void;
    onBrowseExecutable: () => void;
}


export function LaunchOptionsSection(props: LaunchOptionsSectionProps): JSX.Element {
    const s = () => props.settings;

    return (
        <section class="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-3">
            <div class="flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-sm font-semibold text-slate-100">
                        Launch Options
                    </h2>
                    <p class="text-xs text-slate-400 mt-1">
                        Configure how Elite Dangerous is started from this app.
                    </p>
                </div>
                <button
                    class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-medium shadow-sm"
                    onClick={props.onLaunch}
                >
                    Launch game now
                </button>
            </div>

            <div class="flex items-center gap-3">
                <span class="w-32 text-xs text-slate-400 tracking-wide">
                    Launch via
                </span>
                <select
                    class="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-2 py-1 text-xs"
                    value={s().launch_method}
                    onInput={(e) =>
                        props.onUpdateSetting(
                            "launch_method",
                            e.currentTarget.value as LaunchMethod
                        )
                    }
                >
                    <For each={Object.entries(props.launchMethodLabels)}>
                        {([k, v]) => (
                            <option value={k as LaunchMethod}>{v}</option>
                        )}
                    </For>
                </select>
            </div>

            <Show when={s().launch_method === "Executable"}>
                <div class="flex items-center gap-3 mt-2">
                    <span class="w-32 text-xs text-slate-400 tracking-wide">
                        Executable path
                    </span>
                    <input
                        class="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-2 py-1 text-xs placeholder:text-slate-500"
                        readonly
                        value={s().executable_path ?? ""}
                        placeholder="Select the game executable"
                    />
                    <button
                        class="px-3 py-1 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-xs"
                        onClick={props.onBrowseExecutable}
                    >
                        Browse
                    </button>
                </div>
            </Show>

            <Show when={s().launch_method === "Executable" || s().launch_method === "Steam"}>
                <div class="flex items-center gap-3 mt-2">
                    <span class="w-32 text-xs text-slate-400 tracking-wide">
                        Launch arguments
                    </span>
                    <input
                        class="flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-2 py-1 text-xs placeholder:text-slate-500"
                        value={s().launch_arguments}
                        onInput={(e) =>
                            props.onUpdateSetting("launch_arguments", e.currentTarget.value)
                        }
                        placeholder="Optional extra command-line args"
                    />
                </div>
            </Show>

            <label class="inline-flex items-center gap-2 cursor-pointer text-xs pt-2">
                <input
                    type="checkbox"
                    class="rounded border-slate-700 bg-slate-900"
                    checked={s().auto_start_game_on_app_start}
                    onInput={(e) =>
                        props.onUpdateSetting(
                            "auto_start_game_on_app_start",
                            e.currentTarget.checked
                        )
                    }
                />
                <div>
                    <div>Auto start game with this app</div>
                    <div class="text-[11px] text-slate-400">
                        When this companion app starts, automatically launch
                        Elite Dangerous using the selected method.
                    </div>
                </div>
            </label>
        </section>
    );
}
