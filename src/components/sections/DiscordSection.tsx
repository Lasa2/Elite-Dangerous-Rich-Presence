import type { DiscordRichPresenceFields } from "../../../src-tauri/bindings/DiscordRichPresenceFields";
import { SectionHeader, Toggle } from "../ui";

type DiscordSectionProps = {
  discordFields: DiscordRichPresenceFields;
  updateDiscordField: (key: keyof DiscordRichPresenceFields, value: boolean) => void;
};

export function DiscordSection(props: DiscordSectionProps) {
  return (
    <section class="bg-zinc-900/80 border border-zinc-700/40 rounded-lg p-2 shadow-[0_0_12px_rgba(249,115,22,0.04)]">
      <SectionHeader
        title="Discord"
        description="Choose which in-game details appear on your Discord profile."
      />

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-1.5">
        <Toggle
          compact
          label="Commander"
          checked={props.discordFields.commander}
          onChange={(val) => props.updateDiscordField("commander", val)}
        />
        <Toggle
          compact
          label="Superpower"
          checked={props.discordFields.superpower}
          onChange={(val) => props.updateDiscordField("superpower", val)}
        />
        <Toggle
          compact
          label="Location"
          checked={props.discordFields.location}
          onChange={(val) => props.updateDiscordField("location", val)}
        />
        <Toggle
          compact
          label="Gamemode"
          checked={props.discordFields.gamemode}
          onChange={(val) => props.updateDiscordField("gamemode", val)}
        />
        <Toggle
          compact
          label="Multicrew mode"
          checked={props.discordFields.multicrew_mode}
          onChange={(val) => props.updateDiscordField("multicrew_mode", val)}
        />
        <Toggle
          compact
          label="Multicrew size"
          checked={props.discordFields.multicrew_size}
          onChange={(val) => props.updateDiscordField("multicrew_size", val)}
        />
        <Toggle
          compact
          label="Time elapsed"
          checked={props.discordFields.time_elapsed}
          onChange={(val) => props.updateDiscordField("time_elapsed", val)}
        />
        <Toggle
          compact
          label="Ship icon"
          checked={props.discordFields.ship_icon}
          onChange={(val) => props.updateDiscordField("ship_icon", val)}
        />
        <Toggle
          compact
          label="Ship text"
          checked={props.discordFields.ship_text}
          onChange={(val) => props.updateDiscordField("ship_text", val)}
        />
      </div>
    </section>
  );
}
