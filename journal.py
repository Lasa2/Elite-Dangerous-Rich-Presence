import calendar
import configparser
import json
import logging
import logging.config
import msvcrt
import os
import re
import threading
import time

import psutil
from pypresence import Presence

import win32file


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def find_procs_by_name(name):
    "Return a list of processes matching 'name'."
    ls = []
    for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
        if name == p.info['name'] or \
                p.info['exe'] and os.path.basename(p.info['exe']) == name or \
                p.info['cmdline'] and p.info['cmdline'][0] == name:
            ls.append(p)
    return ls


def log(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(name + ".log", encoding="utf8", mode="w")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


class journalPresence:

    def __init__(self):
        _ConfigDefault = {
            "path.journaldir": os.environ["USERPROFILE"] + "/Saved Games/Frontier Developments/Elite Dangerous",
            "richpresence.cmdr": True,
            "richpresence.power": True,
            "richpresence.location": True,
            "richpresence.gamemode": True,
            "richpresence.multiplayertype": True,
            "richpresence.partysize": True,
            "richpresence.timeelapsed": True,
            "richpresence.ship": True
        }
        self.logger = log("JournalPresence")
        self.config = self.loadConfig("config.ini", _ConfigDefault)
        self.journal = []
        self.discordRichPresence = {"Location": "MainMenu", "GameMode": None, "CMDR": None, "Power": None, "LargeImageKey": "elite-dangerous-logo-2018", "PartySize": 1, "MultiplayerType": None, "MultiplayerText": None, "StartTime": calendar.timegm(time.gmtime())}
        self.logger.debug("journalDir: " + self.config["path.journaldir"])
        self.main()

    def main(self):
        self.logger.info("Init Discord Rich Presence")
        self.RPC = Presence(535809971867222036)
        self.RPC.connect()
        process = self.checkRun()
        while process > 0:
            self.stop = False
            if process is 1:
                self.logger.info("Launcher running wait 1 min")
                time.sleep(60)
            elif process is 2:
                self.logger.info("Game running continue loop")
                j = self.getJournal(self.config["path.journaldir"])
                self.startThreads(j)
            process = self.checkRun()
        self.logger.info("Launcher/Game not running stopped loop")
        self.logger.info("Closing Discord Rich Presence Client")
        self.RPC.close()

    def checkRun(self):
        launcher = find_procs_by_name("EDLaunch.exe")
        game = find_procs_by_name("EliteDangerous64.exe")
        if launcher.__len__() > 0:
            if launcher[0].is_running():
                return 1
        if game.__len__() > 0:
            if game[0].is_running():
                return 2
        return 0

    def loadConfig(self, file, config={}):
        """
        returns a dictionary with keys of the form
        <section>.<option> and the corresponding values
        """
        config = config.copy()
        cp = configparser.RawConfigParser()
        cp.read(file)
        for sec in cp.sections():
            name = str.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + str.lower(opt)] = str.strip(cp.get(sec, opt))
                for entry in config:
                    if config[entry] == "true":
                        config[entry] = True
                    elif config[entry] == "false":
                        config[entry] = False
                    try:
                        var = re.search("%(.+?)%", config[entry]).group(1)
                        config[entry] = config[entry].replace("%" + var + "%", os.environ[var])
                    except AttributeError:
                        self.logger.debug("AttributeError with " + str(config[entry]))
                    except TypeError:
                        self.logger.debug("TypeError with " + str(config[entry]))
                    except Exception as e:
                        # catastrophic error. bail.
                        self.logger.critical("Unexpected Error " + str(e))
                        raise SystemExit(e)
        return config

    def getJournal(self, path):
        self.logger.info("Get newest Journal")
        self.logger.info("Journal Directory: " + path)
        nlog = [None, 0]
        try:
            for f in os.listdir(path):
                if "Journal" in f and ".log" in f:
                    timestamp = str(f).replace("Journal.", "")
                    timestamp = timestamp.replace(".log", "")
                    if float(timestamp) > nlog[1]:
                        nlog = f, float(timestamp)
            self.logger.info("Found Journal: " + path + "\\" + nlog[0])
            return path + "\\" + nlog[0]
        except Exception as e:
            # catastrophic error. bail.
            self.logger.critical("Unexpected Error " + str(e))
            raise SystemExit(e)

    def startThreads(self, log):
        self.logger.info("Starting Threads")
        background = self.journalWatcher(log)
        foreground = self.journalReader()
        background.join()
        foreground.join()

    @threaded
    def journalWatcher(self, log):
        handle = win32file.CreateFile(log, win32file.GENERIC_READ, win32file.FILE_SHARE_DELETE | win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, 0, None)
        detached_handle = handle.Detach()
        file_descriptor = msvcrt.open_osfhandle(detached_handle, os.O_RDONLY)
        with open(file_descriptor, encoding="utf-8") as logfile:
            if self.journal == []:
                self.logger.info("First journal read")
                for line in (logfile):
                    self.journal.append(json.loads(line))
            while self.stop is not True:
                for line in (logfile):
                    self.journal.append(json.loads(line))
                    self.logger.debug("Add new journal entry")
                time.sleep(15)
            self.journal = []

    @threaded
    def journalReader(self):
        time.sleep(5)
        self.startupEventsChecks()
        while self.stop is not True:
            self.logger.debug("EventChecks")
            for entry in self.journal:
                if entry["event"] == "Shutdown":
                    self.logger.info("found Event: Shutdown - Breaking Loop")
                    self.stop = True
                elif entry["event"] == "Continued":
                    self.logger.info("found Event: Continued - Breaking Loop")
                    self.stop = True
                self.eventChecks(entry)
            self.presenceUpdate()
            time.sleep(15)

    def startupEventsChecks(self):
        self.logger.info("Startup Journal Check")
        if self.journal[0]["event"] == "Fileheader":
            self.logger.info("found Event: Fileheader")
            for entry in self.journal:
                if entry["event"] == "LoadGame":
                    self.logger.debug("found Event: LoadGame")
                    self.discordRichPresence["CMDR"] = entry["Commander"]
                    self.discordRichPresence["GameMode"] = entry["GameMode"]
                    self.discordRichPresence["LargeImageKey"] = entry["Ship"].lower()
                elif entry["event"] == "Location":
                    self.logger.debug("found Event: Location")
                    Location = entry["StarSystem"]
                    if entry["Docked"] is True:
                        Location = Location + " @ " + entry["StationName"]
                    elif "Body" in entry:
                        Location = entry["Body"]
                    self.discordRichPresence["Location"] = Location
                elif entry["event"] == "Powerplay":
                    self.discordRichPresence["Power"] = entry["Power"]

    def eventChecks(self, entry):
        if entry["event"] == "ApproachBody":
            self.discordRichPresence["Location"] = entry["Body"] + " - Supercruise"
        elif entry["event"] == "Docked":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["StationName"] + "(" + str(int(entry["DistFromStarLS"])) + " ls)"
        elif entry["event"] == "LeaveBody":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " - Supercruise"
        elif entry["event"] == "Location":
            if "StationName" in entry:
                self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["StationName"]
            else:
                self.logger.debug("Ignoring Location Event")
        elif entry["event"] == "SupercruiseEntry":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " - Supercruise"
        elif entry["event"] == "SupercruiseExit":
            if "Body" in entry:
                self.discordRichPresence["Location"] = entry["Body"] + " - Normal Space"
            else:
                self.discordRichPresence["Location"] = entry["StarSystem"] + " - Normal Space"
        elif entry["event"] == "Outfitting":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["StationName"] + " outfitting ship"
        elif entry["event"] == "Shipyard":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["StationName"] + " in the Shipyard"
        elif entry["event"] == "ShipyardNew":
            self.discordRichPresence["LargeImageKey"] = entry["ShipType"].lower()
        elif entry["event"] == "ShipyardSwap":
            self.discordRichPresence["LargeImageKey"] = entry["ShipType"].lower()
        elif entry["event"] == "PowerplayDefect":
            self.discordRichPresence["Power"] = entry["ToPower"]
        elif entry["event"] == "PowerplayJoin":
            self.discordRichPresence["Power"] = entry["Power"]
        elif entry["event"] == "PowerplayLeave":
            self.discordRichPresence["Power"] = None
        elif entry["event"] == "CrewMemberJoins":
            self.discordRichPresence["MultiplayerText"] = "Multicrew Captain"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] + 1
        elif entry["event"] == "CrewMemberQuits":
            self.discordRichPresence["MultiplayerText"] = "Multicrew Captain"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] - 1
        elif entry["event"] == "EndCrewSession":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            self.discordRichPresence["PartySize"] = 1
        elif entry["event"] == "JoinACrew":
            self.discordRichPresence["MultiplayerText"] = "In CMDR´s " + entry["Captain"] + " crew"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = None
        elif entry["event"] == "KickCrewMember":
            self.discordRichPresence["MultiplayerText"] = "Multicrew Captain"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] - 1
        elif entry["event"] == "QuitACrew":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            self.discordRichPresence["PartySize"] = 1
        elif entry["event"] == "WingAdd":
            self.discordRichPresence["MultiplayerText"] = "In Wing"
            self.discordRichPresence["MultiplayerType"] = "Wing"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] + 1
        elif entry["event"] == "WingJoin":
            self.discordRichPresence["MultiplayerText"] = "In Wing"
            self.discordRichPresence["MultiplayerType"] = "Wing"
            count = 0
            for member in entry["Others"]:
                count = count + 1
            self.discordRichPresence["PartySize"] = count + 1
        elif entry["event"] == "WingLeave":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            self.discordRichPresence["PartySize"] = 1
        elif entry["event"] == "FSDJump":
            self.discordRichPresence["Location"] = "In " + entry["StarSystem"]
        elif entry["event"] == "Continued":
            self.status = "New File"

    def presenceUpdate(self):
        self.logger.debug("Update Presence")
        rstate = None
        rdetails = None
        rstart = None
        rlarge_text = None
        rlarge_image = None
        rparty_size = None
        if self.config["richpresence.gamemode"] is True:
            rstate = self.discordRichPresence["GameMode"]
        if self.discordRichPresence["MultiplayerType"] is not None and self.config["richpresence.multiplayertype"] is True:
            rstate = rstate + " | " + self.discordRichPresence["MultiplayerText"]
        if self.config["richpresence.cmdr"] is True and self.discordRichPresence["CMDR"] is not None:
            rlarge_text = "CMDR " + self.discordRichPresence["CMDR"]
        if self.discordRichPresence["Power"] is not None and self.config["richpresence.power"] is True:
            rlarge_text = rlarge_text + " | " + self.discordRichPresence["Power"]
        if self.config["richpresence.timeelapsed"] is True:
            rstart = self.discordRichPresence["StartTime"]
        if self.config["richpresence.location"] is True:
            rdetails = self.discordRichPresence["Location"]
        if self.config["richpresence.ship"] is True:
            rlarge_image = self.discordRichPresence["LargeImageKey"]
        else:
            rlarge_image = "elite-dangerous-logo-2018"
        if self.discordRichPresence["MultiplayerType"] is None:
            rparty_size = None
        elif self.discordRichPresence["MultiplayerType"] == "Multicrew" and self.config["richpresence.partysize"] is True:
            rparty_size = self.discordRichPresence["PartySize"], 3
        elif self.discordRichPresence["MultiplayerType"] == "Wing" and self.config["richpresence.partysize"] is True:
            rparty_size = self.discordRichPresence["PartySize"], 4
        responde = self.RPC.update(state=rstate, details=rdetails, start=rstart, large_text=rlarge_text, large_image=rlarge_image, party_size=rparty_size)
        self.logger.debug(responde)


if __name__ == "__main__":
    reader = journalPresence()
