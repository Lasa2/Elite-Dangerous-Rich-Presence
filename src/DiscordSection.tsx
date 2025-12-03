import type { JSX } from "solid-js";
import type { DiscordRichPresenceFields } from "../src-tauri/bindings/DiscordRichPresenceFields";

interface DiscordSectionProps {
    discord: DiscordRichPresenceFields;
    onUpdateDiscord: <K extends keyof DiscordRichPresenceFields>(
        key: K,
        value: DiscordRichPresenceFields[K]
    ) => void;
}

export function DiscordSection(props: DiscordSectionProps): JSX.Element {
    const d = () => props.discord;

    return (
        <section class="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-3">
            <div class="flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-sm font-semibold text-slate-100">
                        Discord Rich Presence
                    </h2>
                    <p class="text-xs text-slate-400 mt-1">
                        Choose which in-game details you want to show on your Discord profile.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-2 mt-1 text-xs">
                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().commander}
                        onInput={(e) => props.onUpdateDiscord("commander", e.currentTarget.checked)}
                    />
                    <span>Commander name</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().superpower}
                        onInput={(e) =>
                            props.onUpdateDiscord("superpower", e.currentTarget.checked)
                        }
                    />
                    <span>Superpower allegiance</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().location}
                        onInput={(e) =>
                            props.onUpdateDiscord("location", e.currentTarget.checked)
                        }
                    />
                    <span>Location (system / station)</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().gamemode}
                        onInput={(e) =>
                            props.onUpdateDiscord("gamemode", e.currentTarget.checked)
                        }
                    />
                    <span>Game mode (Open / Solo / PG)</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().multicrew_mode}
                        onInput={(e) =>
                            props.onUpdateDiscord("multicrew_mode", e.currentTarget.checked)
                        }
                    />
                    <span>Multicrew activity</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().multicrew_size}
                        onInput={(e) =>
                            props.onUpdateDiscord("multicrew_size", e.currentTarget.checked)
                        }
                    />
                    <span>Multicrew size</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().time_elapsed}
                        onInput={(e) =>
                            props.onUpdateDiscord("time_elapsed", e.currentTarget.checked)
                        }
                    />
                    <span>Elapsed session time</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().ship_icon}
                        onInput={(e) =>
                            props.onUpdateDiscord("ship_icon", e.currentTarget.checked)
                        }
                    />
                    <span>Ship Icon</span>
                </label>

                <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        class="rounded border-slate-700 bg-slate-900"
                        checked={d().ship_text}
                        onInput={(e) =>
                            props.onUpdateDiscord("ship_text", e.currentTarget.checked)
                        }
                    />
                    <span>Ship Text</span>
                </label>
            </div>
        </section>
    );
}
