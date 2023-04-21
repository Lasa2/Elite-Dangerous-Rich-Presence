import msvcrt
import os
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import win32file
from loguru import logger
from pydantic import BaseModel

logger.add(Path("status.log"), level="DEBUG")

DEFAULT_JOURNAL_PATH = Path(
    os.environ["USERPROFILE"],
    "Saved Games",
    "Frontier Developments",
    "Elite Dangerous",
)


def read(file: Path):
    handle = win32file.CreateFile(
        str(file),
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_DELETE
        | win32file.FILE_SHARE_READ
        | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None,
    )
    detached_handle = handle.Detach()
    file_descriptor = msvcrt.open_osfhandle(detached_handle, os.O_RDONLY)

    with open(file_descriptor, encoding="utf-8") as journal:
        last_line = ""
        while True:
            journal.seek(0)
            line = journal.readline()

            if line == last_line:
                sleep(1)
            else:
                last_line = line
                logger.debug(line)


# read(DEFAULT_JOURNAL_PATH / "status.json")


@dataclass(slots=True)
class Flags1:
    docked = False
    landed = False
    landing_gear_up = False
    shields_up = False
    supercruise = False
    flight_assist_off = False
    hardpoints_deployed = False
    in_wing = False
    lights_on = False
    cargo_scoop_deployed = False
    silent_ruinning = False
    scooping_fuel = False
    srv_handbrake = False
    srv_using_turret_view = False
    srv_turret_retracted = False
    srv_drive_assist = False
    fsd_mass_locked = False
    fsd_charging = False
    fsd_cooldown = False
    low_fuel = False
    overheating = False
    has_lat_long = False
    in_danger = False
    being_interdicted = False
    in_main_ship = False
    in_fighter = False
    in_srv = False
    hud_in_analysis_mode = False
    night_vision = False
    altitude_from_average_radius = False
    fsd_jump = False
    srv_high_beam = False


@dataclass(slots=True)
class Flags2:
    on_foot = False
    in_taxi = False
    in_multicrew = False
    on_foot_in_station = False
    on_foot_on_planet = False
    aim_down_sights = False
    low_oxygen = False
    low_health = False
    cold = False
    hot = False
    very_cold = False
    very_hot = False
    glide_mode = False
    on_foot_in_hangar = False
    on_foot_social_space = False
    on_foot_exterior = False
    breathable_atmosphere = False
    telepresence_multicrew = False
    physical_multicrew = False
    fsd_hyperdrive_charging = False


def convert_flags1(flags: int):
    as_str = f"{flags:#033b}"
