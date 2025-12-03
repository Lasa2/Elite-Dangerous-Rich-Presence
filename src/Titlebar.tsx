import type { JSX } from "solid-js";

interface TitlebarProps {
    isMaximized: boolean;
    onMinimize: () => void;
    onToggleMaximize: () => void;
    onClose: () => void;
    onHeaderMouseDown: (e: MouseEvent) => void;
    onHeaderDoubleClick: () => void;
}

export function Titlebar(props: TitlebarProps): JSX.Element {
    return (
        <header
            class="h-11 px-4 flex items-center justify-between border-b border-slate-800 select-none"
            onMouseDown={props.onHeaderMouseDown}
            onDblClick={props.onHeaderDoubleClick}
        >
            <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-emerald-500/70" />
                <span class="text-sm font-medium tracking-tight">
                    Elite Dangerous Rich Presence
                </span>
            </div>

            <div class="flex items-center gap-1 text-slate-400">
                <button
                    class="w-8 h-7 grid place-items-center rounded hover:bg-slate-800/70 text-xs"
                    onMouseDown={(e) => e.stopPropagation()}
                    onClick={props.onMinimize}
                >
                    _
                </button>
                <button
                    class="w-8 h-7 grid place-items-center rounded hover:bg-slate-800/70 text-xs"
                    onMouseDown={(e) => e.stopPropagation()}
                    onClick={props.onToggleMaximize}
                >
                    {props.isMaximized ? "❐" : "☐"}
                </button>
                <button
                    class="w-8 h-7 grid place-items-center rounded hover:bg-red-500/80 hover:text-white text-xs"
                    onMouseDown={(e) => e.stopPropagation()}
                    onClick={props.onClose}
                >
                    ✕
                </button>
            </div>
        </header>
    );
}
