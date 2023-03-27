from enum import Enum, auto
from typing import Any

from loguru import logger

from elite_dangerous_rich_presence.settings_config import settings
from elite_dangerous_rich_presence.util import iso_to_unix

SHIPS = {
    # Player Ships
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
    # Taxi
    "adder_taxt": "Taxi",
}

SUITS = {
    "utilitysuit_class1": "Maverick Suit",
    "explorationsuit_class1": "Artemis Suit",
    "tacticalsuit_class1": "Dominator Suit",
}

SRVS = {
    "testbuggy": "SRV",
    # TODO: Get name of Scrorpion SRV
}

VESSELS = SHIPS | SUITS | SRVS


class Status(Enum):
    LAUNCHER = auto()
    MAIN_MENU = auto()
    DOCKED = auto()
    NORMAL_SPACE = auto()
    SUPERCRUISE = auto()
    LANDED = auto()
    SRV = auto()
    ON_FOOT_STATION = auto()
    ON_FOOT_PLANET = auto()


class EventProcessor:
    starsystem: str = "Launcher"
    body: str | None = None
    status: Status = Status.LAUNCHER
    taxi: bool = False
    game_mode: str | None = None
    cmdr: str | None = None
    power: str | None = None
    ship: str | None = None
    srv: str | None = None
    multicrew_mode: str | None = None
    secs_elapsed: int = 0
    legacy = False

    async def __call__(self, event: dict[str, Any]):
        match event:
            # Startup & shutdown events

            # First entry in journal
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
                self.status = Status.LAUNCHER
                self.ship = None
                self.secs_elapsed = iso_to_unix(timestamp)

            case {
                "event": "LoadGame",
                "Commander": cmdr,
                "Ship": ship,
                "GameMode": gamemode,
            }:
                if ship.lower() in SRVS:
                    self.srv = ship.lower()
                else:
                    self.ship = ship
                self.cmdr = cmdr
                self.game_mode = gamemode

            case {
                "event": "Powerplay",
                "Power": power,
            }:
                self.power = power

            case {
                "event": "Location",
                "StarSystem": starsystem,
                "Docked": docked,
                **data,
            }:
                self.starsystem = starsystem

                if body := data.get("Body"):
                    self.body = body.replace(starsystem, "")

                if "Taxi" in data and data["Taxi"] is True:
                    self.taxi = True

                if "Multicrew" in data and data["Multicrew"] is True:
                    self.multicrew_mode = "Multicrew"

                if docked:
                    self.status = Status.DOCKED
                elif "InSRV" in data:
                    self.status = Status.SRV
                elif "OnFoot" in data:
                    if data["BodyType"] == "Planet":
                        self.status = Status.ON_FOOT_PLANET
                    else:
                        self.status = Status.ON_FOOT_STATION
                else:
                    self.status = Status.NORMAL_SPACE
            # Ingame Events

            # Any time entering the ship
            case {
                "event": "Loadout",
                "Ship": ship,
            }:
                self.ship = ship

            # Docked
            case {
                "event": "Docked",
                "StationName": station,
            }:
                self.status = Status.DOCKED
                self.body = f"@ {station}"

            case {
                "event": "Embark",
                "OnStation": True,
                "StationName": station,
                "Taxi": taxi,
            }:
                self.status = Status.DOCKED
                self.taxi = taxi
                self.body = f"@ {station}"

            # Supercruise
            case {
                "event": "SupercruiseEntry",
            }:
                self.status = Status.SUPERCRUISE

            case {
                "event": "FSDJump",
                "StarSystem": starsystem,
            }:
                self.status = Status.SUPERCRUISE
                self.starsystem = starsystem

            # Supercruise - Near Body
            case {
                "event": "ApproachBody",
                "Body": body,
            }:
                self.body = body.replace(self.starsystem, "")

            case {
                "event": "LeaveBody",
            }:
                self.body = None

            # Normal Space
            case {"event": "Undocked"}:
                self.status = Status.NORMAL_SPACE
                self.body = None

            case {
                "event": "SupercruiseExit",
                "Body": body,
            }:
                self.body = body.replace(self.starsystem, "")
                self.status = Status.NORMAL_SPACE

            case {
                "event": "Liftoff",
                "PlayerControlled": True,
            }:
                self.status = Status.NORMAL_SPACE

            # Landed
            case {
                "event": "Touchdown",
                "PlayerControlled": True,
                "OnPlanet": True,
            }:
                self.status = Status.LANDED

            case {"event": "DockSRV"}:
                self.status = Status.LANDED
                self.srv = None
                # Ship handeled by Loadout event

            case {
                "event": "Embark",
                "OnPlanet": True,
                "SRV": False,
                "Taxi": taxi,
            }:
                self.status = Status.LANDED
                self.taxi = taxi
            # SRV
            case {
                "event": "LaunchSRV",
                "PlayerControlled": True,
                "SRVType": srv,
            }:
                self.status = Status.SRV
                self.srv = srv

            case {
                "event": "Embark",
                "OnPlanet": True,
                "SRV": True,
            }:
                self.status = Status.SRV

            # OnFoot
            case {"event": "SuitLoadout", "SuitName": suit}:
                self.ship = suit

            # OnFoot - Station
            case {
                "event": "Disembark",
                "OnStation": True,
                "Taxi": False,
            }:
                self.status = Status.ON_FOOT_STATION

            case {
                "event": "DropShipDeployed",
                "OnStation": True,
            }:
                self.status = Status.ON_FOOT_STATION

            # OnFoot - Planet
            case {
                "event": "Disembark",
                "OnPlanet": True,
                "Taxi": taxi,
            }:
                self.status = Status.ON_FOOT_PLANET

                if taxi:
                    self.taxi = False
                # Ship handled by SuitLoadout

            case {
                "event": "DropShipDeploy",
                "OnPlanet": True,
            }:
                self.status = Status.ON_FOOT_PLANET

            # Wing
            case {"event": "WingJoin"} | {"event": "WingAdd"}:
                self.multicrew_mode = "Wing"

            case {"event": "WingLeave"}:
                self.multicrew_mode = None

            # Multicew
            case {"event": "EndCrewSession"} | {"event": "QuitACrew"}:
                self.multicrew_mode = None
                self.multicrew_size = 0

            case {"event": "JoinACrew"}:
                self.multicrew_mode = "Multicrew"

            # Powerplay
            case {
                "event": "PowerplayJoin",
                "Power": power,
            } | {
                "event": "PowerplayDefect",
                "ToPower": power,
            }:
                self.power = power

            case {"event": "PowerplayLeave"}:
                self.power = None

            # Various
            case {"event": "CarrierJump", "StarSystem": starsystem}:
                self.starsystem = starsystem

    def rpc_dict(self) -> dict[str, str | None]:
        state: list[str] = []
        details: str | None = None
        start: str | None = None
        large_text: list[str] = []
        large_image = "elite-dangerous-logo-2018"

        conf = settings.rich_presence

        if conf.gamemode and self.game_mode:
            state.append(self.game_mode)

        if conf.multicrew_mode and self.multicrew_mode:
            state.append(self.multicrew_mode)

        if conf.cmdr and self.cmdr:
            large_text.append(f"CMDR {self.cmdr}")

        vessle = self.srv if self.status is Status.SRV else self.ship
        if conf.ship_text and vessle in VESSELS:
            large_text.append(VESSELS[vessle])

        if conf.power and self.power:
            large_text.append(self.power)

        if conf.time_elapsed and self.secs_elapsed:
            start = str(self.secs_elapsed)

        if conf.location:
            details = self.starsystem

            if self.body:
                details += self.body

        if conf.ship_icon and self.ship:
            large_image = self.ship

        return {
            "state": " | ".join(state) or None,
            "details": details,
            "start": start,
            "large_text": " | ".join(large_text) or None,
            "large_image": large_image,
        }
