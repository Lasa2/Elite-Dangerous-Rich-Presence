import { JSX } from "solid-js";

type SectionHeaderProps = {
  title: string;
  description: string;
  rightElement?: JSX.Element;
};

export function SectionHeader(props: SectionHeaderProps) {
  return (
    <div class="mb-1.5 flex items-center justify-between gap-2">
      <div class="flex items-start gap-2">
        <div class="mt-0.5 w-0.5 h-4 rounded-full bg-gradient-to-b from-orange-400/70 via-orange-500/50 to-amber-400/40 shadow-[0_0_4px_rgba(249,115,22,0.4)]" />
        <div>
          <h2 class="text-[13px] font-semibold text-orange-200/90 tracking-tight">
            {props.title}
          </h2>
          <p class="text-[10px] text-zinc-400">{props.description}</p>
        </div>
      </div>

      {props.rightElement && (
        <div class="flex items-center gap-2">{props.rightElement}</div>
      )}
    </div>
  );
}
