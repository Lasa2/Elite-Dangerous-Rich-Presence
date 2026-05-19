import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import { createSignal, JSX } from "solid-js";

export function Titlebar() {
  const webview = getCurrentWebviewWindow();
  const [isMaximized, setIsMaximized] = createSignal<boolean>(false);

  const handleMinimize = async () => {
    await webview.minimize();
  };

  const handleToggleMaximize = async () => {
    await webview.toggleMaximize();
    const max = await webview.isMaximized();
    setIsMaximized(max);
  };

  const handleClose = async () => {
    await webview.close();
  };

  const handleMouseDown = (e: MouseEvent) => {
    if (e.button !== 0) return;
    if (e.detail === 2) return;
    webview.startDragging();
  };

  const handleDoubleClick = async () => {
    await webview.toggleMaximize();
    const max = await webview.isMaximized();
    setIsMaximized(max);
  };

  return (
    <header
      class="flex items-center justify-between px-2 h-8 select-none"
      onMouseDown={handleMouseDown}
      onDblClick={handleDoubleClick}
    >
      <div class="flex items-center gap-2 text-[11px] text-zinc-300">
        <span class="w-1.5 h-1.5 rounded-full bg-orange-400/90 shadow-[0_0_6px_rgba(251,146,60,0.8)]" />
        <span class="font-medium tracking-tight text-orange-100/90">
          Elite Dangerous Rich Presence
        </span>
      </div>

      <div class="flex items-center gap-0.5">
        <TitlebarButton ariaLabel="Minimize window" onClick={handleMinimize}>
          _
        </TitlebarButton>
        <TitlebarButton ariaLabel="Maximize or restore window" onClick={handleToggleMaximize}>
          {isMaximized() ? "🗗" : "🗖"}
        </TitlebarButton>
        <TitlebarButton
          ariaLabel="Close window"
          variant="danger"
          onClick={handleClose}
        >
          X
        </TitlebarButton>
      </div>
    </header>
  );
}

type TitlebarButtonProps = {
  ariaLabel: string;
  children: JSX.Element;
  variant?: "default" | "danger";
  onClick: () => void | Promise<void>;
};

function TitlebarButton(props: TitlebarButtonProps) {
  return (
    <button
      type="button"
      aria-label={props.ariaLabel}
      onClick={props.onClick}
      onMouseDown={(e) => e.stopPropagation()}
      class={`w-7 h-6 flex items-center justify-center text-[11px] rounded-md transition
        ${props.variant === "danger"
          ? "text-red-200 hover:bg-red-600/80 hover:text-white"
          : "text-zinc-300 hover:bg-zinc-800/70 hover:text-orange-200"
        }`}
    >
      {props.children}
    </button>
  );
}
