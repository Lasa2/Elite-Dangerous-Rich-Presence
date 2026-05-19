type ToggleProps = {
  label: string;
  description?: string;
  checked: boolean;
  compact?: boolean;
  onChange: (value: boolean) => void;
};

export function Toggle(props: ToggleProps) {
  return (
    <button
      type="button"
      onClick={() => props.onChange(!props.checked)}
      class={`w-full flex items-center justify-between gap-2.5 rounded-md border bg-zinc-900/70 px-2.5 text-left transition
      border-zinc-700/40 hover:border-orange-400/50 hover:bg-zinc-900/80
      ${props.compact ? "py-0.75" : "py-1"}`}
    >
      <div class="flex-1 min-w-0">
        <p class="text-[11px] font-medium text-zinc-100 truncate">
          {props.label}
        </p>
        {props.description && (
          <p class="text-[10px] text-zinc-500 mt-0.5 line-clamp-2">
            {props.description}
          </p>
        )}
      </div>
      <div
        class={`relative inline-flex h-4 w-8 shrink-0 items-center rounded-full border transition
          ${props.checked
            ? "bg-orange-500/60 border-orange-300/60 shadow-[0_0_6px_rgba(249,115,22,0.4)]"
            : "bg-zinc-700/80 border-zinc-500/60"
          }`}
      >
        <span
          class={`inline-block h-3.5 w-3.5 transform rounded-full bg-zinc-100 shadow-sm transition-transform
            ${props.checked ? "translate-x-4" : "translate-x-1"}`}
        />
      </div>
    </button>
  );
}
