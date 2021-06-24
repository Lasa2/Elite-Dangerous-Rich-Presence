import calendar
import logging
import logging.config
import multiprocessing
import os
import subprocess
import sys
import time
from multiprocessing import Pipe, Process
from typing import Dict

import win32gui
import yaml
from pypresence import Presence

import JournalFileApp
import TrayApp

with open("logging.yaml", "r") as stream:
    try:
        logging_conf = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        raise e
logging.config.dictConfig(logging_conf)
logger = logging.getLogger("BackgroundApp")


def handle_exception(exc_type, exc_value, exc_traceback):
    # if issubclass(exc_type, KeyboardInterrupt):
    #     sys.__excepthook__(exc_type, exc_value, exc_traceback)
    #     return

    logger.error("Uncaught exception", exc_info=(
        exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def save_logging_conf(conf):
    with open("logging.yaml", "w") as stream:
        try:
            stream.write(yaml.dump(conf))
        except yaml.YAMLError as e:
            logger.error("Could not write logging.yaml, %s", e)


def open_settings(con):
    import SettingsApp  # noqa # nopep8
    SettingsApp.SettingsApp(con).run()
    con.send("closed")


def open_journal(con, journal_path):
    JournalFileApp.JournalFileApp(con, journal_path).read_loop()


class EventProcessing():
    location = "Launcher"
    game_mode = None
    cmdr = None
    power = None
    ship = None
    multicrew_size = None
    multicrew_mode = None
    time_elapsed = None
    shipnames = {
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

    def ev(self, e):
        ev = e["event"]
        if ev == "GameShutdown":
            return False
        elif ev == "Launcher":
            self.location = "Launcher"
            self.ship = "elite-dangerous-logo-2018"
            self.time_elapsed = time.strptime(
                e["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            self.game_mode = None
        elif ev == "GameStarted" or ev == "Music" and e["MusicTrack"] == "MainMenu":
            self.time_elapsed = time.strptime(
                e["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            self.location = "Mainmenu"
            self.ship = "elite-dangerous-logo-2018"
            self.game_mode = None
        elif ev == "LoadGame" and e.get("GameMode", None):
            self.cmdr = e["Commander"]
            self.game_mode = e["GameMode"]
            self.ship = e["Ship"].lower()
        elif ev == "Location" or ev == "SupercruiseExit":
            if "Docked" in e:
                if e["Docked"]:
                    self.location = f'{e["StarSystem"]} @ {e["StationName"]}'
                    if "DistFromStarLs" in e:
                        self.location += f' ({e["DistFromStarLS"]} ls)'
            elif "Body" in e:
                if e["BodyType"] == "Station":
                    self.location = f'{e["StarSystem"]} @ {e["Body"]}'
                else:
                    self.location = f'{e["Body"]} - Normal Space'
            else:
                self.location = f'{e["StarSystem"]} - Normal Space'
        elif ev == "ApproachBody":
            self.location = f'{e["Body"]} - Supercruise'
        elif ev == "Docked":
            self.location = f'{e["StarSystem"]} @ {e["StationName"]} ({e["DistFromStarLS"]} ls)'
        elif ev == "Undocked":
            self.location = self.location.replace("- Landed", "")
        elif ev == "LeaveBody" or ev == "SupercruiseEntry" or ev == "FSDJump":
            self.location = f'{e["StarSystem"]} - Supercruise'
        elif ev == "Outfitting":
            self.location = f'{e["StarSystem"]} @ {e["StationName"]} outfitting ship'
        elif ev == "Shipyard":
            self.location = f'{e["StarSystem"]} @ {e["StationName"]} in the shipyard'
        elif ev == "ShipyardNew" or ev == "ShipyardSwap":
            self.ship = e["ShipType"].lower()
        elif ev == "Powerplay" or ev == "PowerplayJoin":
            self.power = e["Power"]
        elif ev == "PowerplayDefect":
            self.power = e["ToPower"]
        elif ev == "PowerplayLeave":
            self.power = None
        elif ev == "CrewMemberJoins":
            self.multicrew_mode = "Multicrew"
            self.multicrew_size += 1
        elif ev == "CrewMemberQuits":
            self.multicrew_size -= 1
        elif ev == "EndCrewSession":
            self.multicrew_mode = None
            self.multicrew_size = None
        elif ev == "KickCrewMember":
            self.multicrew_size -= 1
        elif ev == "JoinACrew":
            self.multicrew_mode = "Multicrew"
        elif ev == "QuitACrew":
            self.multicrew_mode = None
        elif ev == "WingAdd" or ev == "WingJoin":
            self.multicrew_mode = "In a Wing"
        elif ev == "WingLeave":
            self.multicrew_mode = None
        elif ev == "LaunchSRV":
            if e["PlayerControlled"]:
                self.ship = "testbuggy"
                self.location = "- ".join(self.location.split("-")[:-1]) + "- SRV"
        elif ev == "DockSRV":
            self.location = "- ".join(self.location.split("-")[:-1]) + "- Landed"
        elif ev == "Touchdown":
            if e["PlayerControlled"]:
                self.location = "- ".join(self.location.split("-")[:-1]) + "- Landed"
        elif ev == "Liftoff":
            if e["PlayerControlled"]:
                self.location = "- ".join(self.location.split("-")[:-1]) + "- Normal Space"
        elif ev == "Loadout":
            self.ship = e["Ship"].lower()
        elif ev == "SuitLoadout":
            self.ship = e["SuitName"]
            if "-" in self.location:
                self.location = "- ".join(self.location.split("-")[:-1]) + "- On foot"
        elif ev == "Embark":
            if e["SRV"]:
                self.ship = "testbuggy"
                self.location = "- ".join(self.location.split("-")[:-1]) + "- SRV"
            else:
                self.location = "- ".join(self.location.split("-")[:-1]) + "- Landed"
        elif ev == "Music" and e["MusicTrack"] == "CQCMenu":
            self.location = "CQC"

        return True

    def rpc(self, conf):
        state = None
        details = None
        start: time.struct_time = None
        large_text = None
        large_image = "elite-dangerous-logo-2018"
        party_size = None

        if conf["gamemode"] and self.game_mode:
            state = self.game_mode
        if conf["multicrew_mode"] and self.multicrew_mode:
            state = state + f" | {self.multicrew_mode}" if state else self.multicrew_mode
        if conf["cmdr"] and self.cmdr:
            large_text = f"CMDR {self.cmdr}"
        if conf["ship_text"] and self.ship in self.shipnames:
            large_text = large_text + f" | {self.shipnames[self.ship]}" if large_text else self.shipnames[self.ship]
        if conf["power"] and self.power:
            large_text = large_text + f" | {self.power}" if large_text else self.power
        if conf["time_elapsed"] and self.time_elapsed:
            start = str(calendar.timegm(self.time_elapsed))
        if conf["location"] and self.location:
            details = self.location
        if conf["ship_icon"] and self.ship:
            large_image = self.ship
        if conf["multicrew_size"] and self.multicrew_size:
            party_size = self.multicrew_size

        return state, details, start, large_text, large_image, party_size


class BackgroundApp():
    open_settings: bool = False
    config: Dict = {
        "general": {
            "auto_tray": False,
            "journal_path": os.path.join(os.environ["USERPROFILE"], "Saved Games\\Frontier Developments\\Elite Dangerous"),
            "log_level": "WARNING",
        },
        "rich_presence": {
            "cmdr": True,
            "power": True,
            "location": True,
            "gamemode": True,
            "multicrew_mode": True,
            "multicrew_size": True,
            "time_elapsed": True,
            "ship_icon": True,
            "ship_text": True,
        },
        "elite_dangerous": {
            "path": "",
            "arguments": "",
            "auto_launch": False,
        }
    }

    def __init__(self) -> None:
        self.load_config()
        self.ev = EventProcessing()
        logger.info("Runing Elite Dangerous Rich Presence V4.6")

    def load_config(self):
        if not os.path.isfile("settings.yaml"):
            with open("settings.yaml", "w") as stream:
                try:
                    stream.write(yaml.dump(self.config))
                except yaml.YAMLError as e:
                    logger.exception("Could not write settings.yaml, %s", e)
                    raise e
        with open("settings.yaml", "r") as stream:
            try:
                data = yaml.safe_load(stream)
                self.config = data
            except yaml.YAMLError as e:
                logger.exception("Could not load settings.yaml, %s", e)
                raise e
        logging_conf["root"]["level"] = self.config["general"]["log_level"]
        logging.getLogger().setLevel(self.config["general"]["log_level"])
        save_logging_conf(logging_conf)

    def event_processing(self, event):
        game = self.ev.ev(event)
        if not game:
            return game
        state, details, start, large_text, large_image, party_size = self.ev.rpc(
            self.config["rich_presence"])
        self.rpc.update(state=state, details=details, start=start,
                        large_text=large_text, large_image=large_image, party_size=party_size)
        return game

    def open_settings_call(self):
        if self.open_settings:
            self.settings_parent_con.send("restore")
        else:
            self.open_settings = True

    def launch_ed(self):
        if JournalFileApp.getLauncher() or JournalFileApp.getGame():
            logger.info("Elite already running")
            return
        if self.config["elite_dangerous"]["path"].endswith(".exe"):
            logger.debug("Lauch executable: %s with arguments: %s",
                         self.config["elite_dangerous"]["path"], self.config["elite_dangerous"]["arguments"])
            try:
                game = self.config["elite_dangerous"]["path"] + \
                    " " + self.config["elite_dangerous"]["arguments"]
                subprocess.Popen(game)
                logger.debug(
                    "Launched executable, now waiting for Elite Launcher")
            except Exception as e:
                logger.error("Unable to launch executable, %s", e)
        else:
            logger.debug("Lauch: %s without arguments",
                         self.config["elite_dangerous"]["path"])
            try:
                os.system(f'"{self.config["elite_dangerous"]["path"]}"')
                logger.debug(
                    "Launched, now waiting for Elite Launcher")
            except Exception as e:
                logger.error("Unable to launch executable, %s", e)
        code = 0
        while not JournalFileApp.getLauncher() and code == 0:
            code = win32gui.PumpWaitingMessages()
            time.sleep(0.1)
        logger.debug("Elite Launcher running, continuing")

    def run(self):
        TrayApp.TrayApp(self.open_settings_call,
                        name="Elite Dangerous Rich Presence", icon="elite-dangerous-clean.ico")

        logger.debug("Starting Rich Presence")
        self.rpc = Presence(535809971867222036)
        self.rpc.connect()

        # elite dangerous auto launch
        if self.config["elite_dangerous"]["auto_launch"] and os.path.exists(self.config["elite_dangerous"]["path"]):
            self.launch_ed()

        logger.debug("Preparing Tray Application")
        journal_parent_con, journal_child_con = Pipe()
        journal_app = Process(target=open_journal, args=(
            journal_child_con, self.config["general"]["journal_path"]))
        journal_app.start()
        logger.debug("Tray Application stated, continuing")

        logger.debug("Preparing Settings Window")
        self.settings_parent_con, settings_child_con = Pipe()
        app_settings = Process(target=open_settings,
                               args=(settings_child_con,))

        if not self.config["general"]["auto_tray"]:
            app_settings.start()
        logger.debug("Prepared Settings Window")

        code = 0
        game = True
        logger.info("Entering main loop")
        while code == 0 and game:
            code = win32gui.PumpWaitingMessages()

            if self.open_settings and not app_settings.is_alive():
                logger.debug("Opening Settings")
                app_settings.start()

            if self.settings_parent_con.poll():
                msg = self.settings_parent_con.recv()
                if msg == "closed":
                    app_settings = Process(
                        target=open_settings, args=(settings_child_con,))
                    self.open_settings = False
                elif msg == "changed_settings":
                    logger.debug("Config changed, reloading")
                    self.load_config()

            if journal_parent_con.poll():
                msg = journal_parent_con.recv()
                game = self.event_processing(msg)

            time.sleep(0.1)

        self.settings_parent_con.send("closed")
        journal_parent_con.send("closed")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    BackgroundApp().run()
