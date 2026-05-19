import { JSX } from "solid-js";

type ButtonProps = {
  children: JSX.Element;
  onClick: () => void | Promise<void>;
  variant?: "default" | "primary" | "danger";
  disabled?: boolean;
  size?: "sm" | "md";
};

export function Button(props: ButtonProps) {
  const variantClasses = () => {
    switch (props.variant) {
      case "primary":
        return "border-orange-500/60 text-orange-100 bg-zinc-900/80 hover:bg-orange-500/80 hover:text-black";
      case "danger":
        return "border-red-500/60 text-red-200 bg-red-900/40 hover:bg-red-900/70";
      default:
        return "border-zinc-700/40 bg-zinc-900/70 hover:border-orange-400/50 hover:text-orange-200";
    }
  };

  const sizeClasses = () => {
    switch (props.size) {
      case "sm":
        return "h-7 px-3 text-[11px]";
      default:
        return "h-8 px-3 text-[11px]";
    }
  };

  return (
    <button
      type="button"
      disabled={props.disabled}
      onClick={props.onClick}
      class={`rounded-md border transition flex items-center disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses()} ${sizeClasses()}`}
    >
      {props.children}
    </button>
  );
}
