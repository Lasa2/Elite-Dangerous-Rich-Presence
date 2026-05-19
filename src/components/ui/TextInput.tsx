type TextInputProps = {
  label: string;
  value: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  description?: string;
  rightElement?: any;
};

export function TextInput(props: TextInputProps) {
  return (
    <div class="space-y-1">
      <div class="flex items-center justify-between text-[11px]">
        <label class="font-medium text-zinc-300">{props.label}</label>
        {props.description && (
          <span class="text-[10px] text-zinc-500">{props.description}</span>
        )}
      </div>
      <div class="flex items-center gap-2">
        <input
          type="text"
          readOnly={props.readOnly}
          disabled={props.disabled}
          placeholder={props.placeholder}
          class="flex-1 h-8 bg-zinc-900/70 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-orange-400 focus:border-orange-400 disabled:opacity-50 disabled:cursor-not-allowed select-text"
          value={props.value}
          onInput={(e) => props.onChange?.(e.currentTarget.value)}
        />
        {props.rightElement}
      </div>
    </div>
  );
}
