import asyncio
import calendar
import json
import logging
import msvcrt
import os
import time

import win32file
import win32gui


class watch():
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.discordRichPresence = {"Location": "MainMenu", "GameMode": None, "CMDR": None, "Power": None, "LargeImageKey": "elite-dangerous-logo-2018", "PartySize": 0, "MultiplayerType": None, "MultiplayerText": None, "StartTime": calendar.timegm(time.gmtime())}

    async def main(self):
        self.logger.info("Started Background Thread")
        self.mainThread = True
        self.stop = True
        while self.getLauncher() and self.mainThread is True:
            self.logger.info("Launcher running")
            self.stop = False
            self.discordRichPresence["Location"] = "Launcher"
            self.discordRichPresence["GameMode"] = None
            self.discordRichPresence["CMDR"] = None
            self.discordRichPresence["Power"] = None
            self.discordRichPresence["LargeImageKey"] = "elite-dangerous-logo-2018"
            self.discordRichPresence["PartySize"] = 0
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            while self.getGame() and self.mainThread is True:
                self.logger.info("Game running")
                self.stop = False
                self.journal = []
                self.getJournal()
                self.logger.debug("Starting Asyncio Tasks")
                readTask = asyncio.create_task(self.readJournal())
                pushTask = asyncio.create_task(self.journalCheck())
                await readTask
                await pushTask
                self.logger.debug("Asyncio Tasks complete")
            await asyncio.sleep(15)
        self.logger.info("Closing Background Thread")

    def mainThreadStopped(self):
        self.logger.info("Main Thread Stopped")
        self.mainThread = False

    def getJournal(self):
        self.active_file = (0, None)
        self.logger.debug("Scanning in " + self.config["path.journaldir"])
        with os.scandir(self.config["path.journaldir"]) as it:
            self.logger.debug(it)
            for entry in it:
                self.logger.debug(entry)
                if entry.is_file() and "Journal" in entry.name and ".log" in entry.name:
                    new = str.replace(entry.name, "Journal.", "")
                    new = str.replace(new, ".log", "")
                    if float(new) > float(self.active_file[0]):
                        self.active_file = (float(new), entry.name)
        self.logger.debug("Active File: " + self.active_file[1])

    def getLauncher(self):
        if win32gui.FindWindow(None, "Elite Dangerous Launcher"):
            self.logger.debug("Found Launcher Window")
            return True
        else:
            return False

    def getGame(self):
        if win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)"):
            self.logger.debug("Found Game Window")
            return True
        else:
            return False

    async def readJournal(self):
        journal = os.path.join(self.config["path.journaldir"], self.active_file[1])
        handle = win32file.CreateFile(journal, win32file.GENERIC_READ, win32file.FILE_SHARE_DELETE | win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, 0, None)
        detached_handle = handle.Detach()
        file_descriptor = msvcrt.open_osfhandle(detached_handle, os.O_RDONLY)

        with open(file_descriptor, encoding="utf-8") as logfile:
            self.logger.debug("reading journal " + self.active_file[1])
            while self.stop is not True and self.mainThread is True:
                for line in (logfile):
                    self.journal.append(json.loads(line))
                    self.logger.debug("Add new journal entrys")
                await asyncio.sleep(15)

    async def journalCheck(self):
        while self.stop is not True and self.mainThread is True:
            self.logger.debug("EventChecks")
            for entry in self.journal:
                if entry["event"] == "Shutdown":
                    self.logger.info("found Event: Shutdown - Breaking Loop")
                    self.stop = True
                elif entry["event"] == "Continued":
                    self.logger.info("found Event: Continued - Breaking Loop to find new file")
                    self.stop = True
                self.eventChecks(entry)
            await asyncio.sleep(15)
            if self.getGame() is not True:
                self.stop = True

    def eventChecks(self, entry):
        if entry["event"] == "Music" and entry["MusicTrack"] == "MainMenu":
            self.discordRichPresence["Location"] = "Mainmenu"
            self.discordRichPresence["GameMode"] = None
            self.discordRichPresence["CMDR"] = None
            self.discordRichPresence["Power"] = None
            self.discordRichPresence["LargeImageKey"] = "elite-dangerous-logo-2018"
            self.discordRichPresence["PartySize"] = 0
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
        if entry["event"] == "LoadGame":
            self.discordRichPresence["CMDR"] = entry["Commander"]
            self.discordRichPresence["GameMode"] = entry["GameMode"]
            self.discordRichPresence["LargeImageKey"] = entry["Ship"].lower()
        elif entry["event"] == "Location":
            if "Body" in entry:
                if entry["BodyType"] == "Station":
                    self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["Body"]
                else:
                    self.discordRichPresence["Location"] = entry["Body"] + " - Normal Space"
            else:
                self.discordRichPresence["Location"] = entry["StarSystem"] + " - Normal Space"
        elif entry["event"] == "Powerplay":
            self.discordRichPresence["Power"] = entry["Power"]
        if entry["event"] == "ApproachBody":
            self.discordRichPresence["Location"] = entry["Body"] + " - Supercruise"
        elif entry["event"] == "Docked":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["StationName"] + "(" + str(int(entry["DistFromStarLS"])) + " ls)"
        elif entry["event"] == "LeaveBody":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " - Supercruise"
        elif entry["event"] == "SupercruiseEntry":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " - Supercruise"
        elif entry["event"] == "SupercruiseExit":
            if "Body" in entry:
                if entry["BodyType"] == "Station":
                    self.discordRichPresence["Location"] = entry["StarSystem"] + " @ " + entry["Body"]
                else:
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
            self.discordRichPresence["MultiplayerText"] = "Multicrew"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] + 1
        elif entry["event"] == "CrewMemberQuits":
            self.discordRichPresence["MultiplayerText"] = "Multicrew"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] - 1
        elif entry["event"] == "EndCrewSession":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            self.discordRichPresence["PartySize"] = 0
        elif entry["event"] == "JoinACrew":
            self.discordRichPresence["MultiplayerText"] = "Multicrew"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = 0
        elif entry["event"] == "KickCrewMember":
            self.discordRichPresence["MultiplayerText"] = "Multicrew"
            self.discordRichPresence["MultiplayerType"] = "Multicrew"
            self.discordRichPresence["PartySize"] = self.discordRichPresence["PartySize"] - 1
        elif entry["event"] == "QuitACrew":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
            self.config["richpresence.partysize"] = 0
        elif entry["event"] == "WingAdd":
            self.discordRichPresence["MultiplayerText"] = "In a Wing"
            self.discordRichPresence["MultiplayerType"] = "Wing"
        elif entry["event"] == "WingJoin":
            self.discordRichPresence["MultiplayerText"] = "In a Wing"
            self.discordRichPresence["MultiplayerType"] = "Wing"
        elif entry["event"] == "WingLeave":
            self.discordRichPresence["MultiplayerType"] = None
            self.discordRichPresence["MultiplayerText"] = None
        elif entry["event"] == "FSDJump":
            self.discordRichPresence["Location"] = entry["StarSystem"] + " - Supercruise"
        elif entry["event"] == "Touchdown":
            self.discordRichPresence["Location"] = str.replace(self.discordRichPresence["Location"], " - Normal Space", " - Landed")
        elif entry["event"] == "LaunchSRV":
            self.discordRichPresence["LargeImageKey"] = "testbuggy"
        elif entry["event"] == "Liftoff":
            str.replace(self.discordRichPresence["Location"], " - Landed", " - Normal Space")
        elif entry["event"] == "ApproachSettlement":
            self.discordRichPresence["Location"] = str.replace(self.discordRichPresence["Location"], " - Normal Space", " @ " + entry["Name"])
        elif entry["event"] == "Loadout":
            self.discordRichPresence["LargeImageKey"] = entry["Ship"].lower()

    def presenceUpdate(self):
        rstate = None
        rdetails = None
        rstart = None
        rlarge_text = None
        rlarge_image = None
        rparty_size = None
        if self.config["richpresence.gamemode"] is True:
            rstate = self.discordRichPresence["GameMode"]
        if self.discordRichPresence["MultiplayerType"] is not None and self.config["richpresence.multiplayertype"] is True:
            rstate = self.discordRichPresence["MultiplayerText"]
        if self.config["richpresence.cmdr"] is True and self.discordRichPresence["CMDR"] is not None:
            rlarge_text = "CMDR " + self.discordRichPresence["CMDR"]
        if self.discordRichPresence["Power"] is not None and self.config["richpresence.power"] is True:
            rlarge_text = rlarge_text + " | " + self.discordRichPresence["Power"]
        if self.config["richpresence.timeelapsed"] is True:
            rstart = self.discordRichPresence["StartTime"]
        if self.config["richpresence.location"] is True:
            rdetails = self.discordRichPresence["Location"]
        if self.config["richpresence.ship"] is True and self.discordRichPresence["LargeImageKey"]:
            rlarge_image = self.discordRichPresence["LargeImageKey"]
        else:
            rlarge_image = "elite-dangerous-logo-2018"
        if self.config["richpresence.partysize"] == 0:
            rparty_size = None
        elif self.discordRichPresence["MultiplayerType"] == "Multicrew" and self.config["richpresence.partysize"] is not None:
            rparty_size = self.discordRichPresence["PartySize"], 3

        return {"state": rstate, "details": rdetails, "start": rstart, "large_text": rlarge_text, "large_image": rlarge_image, "party_size": rparty_size}
        # self.logger.info(f"state={rstate}, details={rdetails}, start={rstart}, large_text={rlarge_text}, large_image={rlarge_image}, party_size={rparty_size}")
        # responde = self.RPC.update(state=rstate, details=rdetails, start=rstart, large_text=rlarge_text, large_image=rlarge_image, party_size=rparty_size)
        # self.logger.debug(responde)
