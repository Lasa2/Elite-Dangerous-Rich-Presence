from typing import Any

from loguru import logger

from elite_dangerous_rich_presence.settings_config import settings
from elite_dangerous_rich_presence.util import iso_to_unix

SHIPNAMES = {
    "sidewinder": "Sidewinder",
    "eagle": "Eagle",
    "hauler": "Hauler",
    "adder": "Adder",
    "empire_eagle": "Imperial Eagle",
    "viper": "Viper Mk III",
    "cobramkiii": "Cobra Mk III",
    "viper_mkiv": "Viper Mk IV",
    "diamondback": "Diamondback Scout",
    "cobramkiv": "Cobra Mk IV",
    "type6": "Type-6 Transporter",
    "dolphin": "Dolphin",
    "diamondbackxl": "Diamondback Explorer",
    "empire_courier": "Imperial Courier",
    "independant_trader": "Keelback",
    "asp_scout": "Asp Scout",
    "vulture": "Vulture",
    "asp": "Asp Explorer",
    "federation_dropship": "Federal Dropship",
    "type7": "Type-7 Transporter",
    "typex": "Alliance Chieftain",
    "federation_dropship_mkii": "Federal Assault Ship",
    "empire_trader": "Imperial Clipper",
    "typex_2": "Alliance Crusader",
    "typeex_3": "Alliance Challenger",
    "federation_gunship": "Federal Gunship",
    "krait_light": "Krait Phantom",
    "krait_mkii": "Krait Mk II",
    "orca": "Orca",
    "ferdelance": "Fer-de-Lance",
    "mamba": "Mamba",
    "python": "Python",
    "type9": "Type-9 Heavy",
    "belugaliner": "Beluga Liner",
    "type9_military": "Type-10 Defender",
    "anaconda": "Anaconda",
    "federation_corvette": "Federal Corvette",
    "cutter": "Imperial Cutter",
    "testbuggy": "SRV",
    "utilitysuit_class1": "Maverick Suit",
    "explorationsuit_class1": "Artemis Suit",
    "tacticalsuit_class1": "Dominator Suit",
}


class EventProcessor:
    location: str = "Launcher"
    game_mode: str | None = None
    cmdr: str | None = None
    power: str | None = None
    ship: str | None = None
    multicrew_size: int = 0
    multicrew_mode: str | None = None
    secs_elapsed: int = 0
    legacy = False

    async def __call__(self, event: dict[str, Any]):
        match event:

            case {
                "event": "Fileheader",
                "timestamp": timestamp,
                "gameversion": game_version,
                "build": build,
            }:
                logger.info(
                    "Elite Dangerous - Version: {version}, Build: {build} - {timestamp} ",
                    version=game_version,
                    build=build,
                    timestamp=timestamp,
                )
                if game_version.startswith("3.8"):
                    self.legacy = True
                    logger.debug("Enabled Legacy Mode")

            case (
                {"event": "Shutdown", "timestamp": timestamp}
                | {"event": "Launcher", "timestamp": timestamp}
            ):
                self.location = "Launcher"
                self.ship = None
                self.secs_elapsed = iso_to_unix(timestamp)

    def rpc_dict(self) -> dict[str, str | None]:
        state: list[str] = []
        details: str | None = None
        start: str | None = None
        large_text: list[str] = []
        large_image = "elite-dangerous-logo-2018"
        party_size: str | None = None

        conf = settings.rich_presence

        if conf.gamemode and self.game_mode:
            state.append(self.game_mode)

        if conf.multicrew_mode and self.multicrew_mode:
            state.append(self.multicrew_mode)

        if conf.cmdr and self.cmdr:
            large_text.append(f"CMDR {self.cmdr}")

        if conf.ship_text and self.ship in SHIPNAMES:
            large_text.append(SHIPNAMES[self.ship])

        if conf.power and self.power:
            large_text.append(self.power)

        if conf.time_elapsed and self.secs_elapsed:
            start = str(self.secs_elapsed)

        if conf.location and self.location:
            details = self.location

        if conf.ship_icon and self.ship:
            large_image = self.ship

        if conf.multicrew_size and self.multicrew_size:
            party_size = str(self.multicrew_size)

        return {
            "state": " | ".join(state) or None,
            "details": details,
            "start": start,
            "large_text": " | ".join(large_text) or None,
            "large_image": large_image,
            "party_size": party_size,
        }
