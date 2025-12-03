import type { JSX } from "solid-js";
import type { Settings } from "../src-tauri/bindings/Settings";

interface GeneralSectionProps {
    settings: Settings;
    onUpdateSetting: <K extends keyof Settings>(
        key: K,
        value: Settings[K]
    ) => void;
    onSetLaunchOnStartup: (enabled: boolean) => void;
}

export function GeneralSection(props: GeneralSectionProps): JSX.Element {
    const s = () => props.settings;

    return (
        <section class="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-3">
            <div class="flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-sm font-semibold text-slate-100">General</h2>
                    <p class="text-xs text-slate-400 mt-1">
                        Overall behavior of the desktop companion app.
                    </p>
                </div>
            </div>

            <div class="flex flex-col gap-2 pt-1">
                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={s().launch_on_system_startup}
                        onInput={(e) => props.onSetLaunchOnStartup(e.currentTarget.checked)}
                    />
                    <div>
                        <div>Start with Windows</div>
                        <div class="text-xs text-slate-400">
                            Launch this app automatically when your PC starts.
                        </div>
                    </div>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={s().start_to_tray}
                        onInput={(e) =>
                            props.onUpdateSetting("start_to_tray", e.currentTarget.checked)
                        }
                    />
                    <div>
                        <div>Start minimized to tray</div>
                        <div class="text-xs text-slate-400">
                            Keep the window hidden and only show a tray icon on startup.
                        </div>
                    </div>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={s().close_with_game}
                        onInput={(e) =>
                            props.onUpdateSetting("close_with_game", e.currentTarget.checked)
                        }
                    />
                    <div>
                        <div>Close app when game closes</div>
                        <div class="text-xs text-slate-400">
                            Automatically exit this app when Elite Dangerous is no longer running.
                        </div>
                    </div>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={s().check_for_updates}
                        onInput={(e) =>
                            props.onUpdateSetting(
                                "check_for_updates",
                                e.currentTarget.checked
                            )
                        }
                    />
                    <div>
                        <div>Check for app updates</div>
                        <div class="text-xs text-slate-400">
                            Periodically check for new versions of this companion app.
                        </div>
                    </div>
                </label>
            </div>
        </section>
    );
}
