import json
import os
from pathlib import Path

journal_dir = Path(
    os.environ["USERPROFILE"],
    "Saved Games",
    "Frontier Developments",
    "Elite Dangerous",
)

out_dir = Path("./filtered_journals")

filter_events = [
    "Fileheader",
    "Shutdown",
    "Commander",
    "NewCommander",
    "Loadout",
    "LoadGame",
    "Powerplay",
    "ApproachBody",
    "Docked",
    "FSDJump",
    "LeaveBody",
    "Liftoff",
    "Location",
    "SupercruiseExit",
    "SupercruiseEntry",
    "Touchdown",
    "Undocked",
    "Interdicted",
    "Interdiction",
    "SRVDestroyed",
    "ShipyardSwap",
    "PowerplayDefect",
    "PowerplayJoin",
    "PowerplayLeave",
    "CarrierJump",
    "DropShipDeploy",
    "Embark",
    "Disembark",
    "SuitLoadout",
    "ApproachSettlement",
    "Continued",
    "CrewMemberJoins",
    "CrewMemberQuits",
    "DockFighter",
    "DockSRV",
    "EndCrewSession",
    "JoinACrew",
    "KickCrewMember",
    "LaunchFighter",
    "LaunchSRV",
    "QuitACrew",
    "Shutdown",
    "VehicleSwitch",
    "WingAdd",
    "WingJoin",
    "WingLeave",
]

out_dir.mkdir(parents=True, exist_ok=True)

for entry in out_dir.iterdir():
    entry.unlink()

for entry in journal_dir.glob("Journal*.log"):
    data: list[dict] = []
    for line in entry.read_text().splitlines():
        event = json.loads(line)

        if event["event"] in filter_events:
            data.append(event)

    out_file = out_dir / f"{entry.stem}.json"
    out_file.write_text(json.dumps(data))
