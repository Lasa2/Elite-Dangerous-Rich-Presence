import { JSX } from "solid-js";

type SelectProps<T extends string> = {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
  description?: string;
};

export function Select<T extends string>(props: SelectProps<T>) {
  return (
    <div class="space-y-1">
      <label class="text-[11px] leading-none font-medium text-zinc-300">
        {props.label}
      </label>
      <select
        class="ed-select w-full h-8 border border-zinc-700/40 rounded-md px-2.5 text-[11px] focus:outline-none focus:ring-1 focus:ring-orange-400 focus:border-orange-400"
        value={props.value}
        onChange={(e) => props.onChange(e.currentTarget.value as T)}
      >
        {props.options.map((opt) => (
          <option value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {props.description && (
        <p class="text-[10px] text-zinc-500">{props.description}</p>
      )}
    </div>
  );
}
