import asyncio
import configparser
import logging
import logging.config
import os
import re
import threading
import subprocess

import PySimpleGUIQt as sg
import yaml
from pypresence import Presence

from watch import watch

CONFIGDEFAULT = {
    "path.journaldir": os.environ["USERPROFILE"] + "/Saved Games/Frontier Developments/Elite Dangerous",
    "richpresence.cmdr": True,
    "richpresence.power": True,
    "richpresence.location": True,
    "richpresence.gamemode": True,
    "richpresence.multiplayertype": True,
    "richpresence.partysize": True,
    "richpresence.timeelapsed": True,
    "richpresence.ship": True,
    "rungame.path": "S:/SteamLibrary/steamapps/common/Elite Dangerous/EDLaunch.exe",
    "rungame.run": True,
}
CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/logging.yaml"


def log():
    with open(CONFIG, "r") as f:
        log_cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger("info")
    return logger


def loadConfig(file, config={}):
    logger = logging.getLogger(__name__)
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
                    logger.debug("AttributeError with " + str(config[entry]))
                except TypeError:
                    logger.debug("TypeError with " + str(config[entry]))
                except Exception as e:
                    logger.critical("Unexpected Error " + str(e))
                    raise SystemExit(e)
    return config


class gui():
    def __init__(self):
        config = loadConfig("config.ini", config=CONFIGDEFAULT)
        self.rungame = config["rungame.run"], config["rungame.path"]
        self.logger = log()
        self.watch = watch(config)
        self.RPC = Presence(535809971867222036)
        self.RPC.connect()
        self.main()

    def main(self):
        self.logger.debug("Start Main Loop")
        self.main_thread = True
        thread = threading.Thread(target=self.background, args=())
        thread.start()
        menu_def = ["BLANK", "Exit"]
        tray = sg.SystemTray(menu=menu_def, filename='./elite-dangerous-clean.ico', tooltip="Elite Dangerous Rich Presence")
        while self.main_thread is True:  # The event loop
            menu_item = tray.Read(timeout=15000)
            if menu_item == 'Exit':
                self.watch.mainThreadStopped()
                break
            data = self.watch.presenceUpdate()
            responde = self.RPC.update(state=data["state"], details=data["details"], start=data["start"], large_text=data["large_text"], large_image=data["large_image"], party_size=data["party_size"])
        self.RPC.close()
        self.logger.debug("Main Loop Complete")

    def background(self):
        self.logger.debug("Check if the Game should be started")
        if self.watch.getGame() is False and self.watch.getLauncher() is False and self.rungame[0] is True:
            if os.path.exists(self.rungame[1]):
                self.logger.debug("Game Path exists")
                try:
                    subprocess.run(self.rungame[1])
                except Exception as e:
                    self.logger.error("Could not start Game: " + e)
            else:
                self.logger.warning("Game Path doesnt exists")
        self.logger.debug("Start Background Loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.watch.main())
        loop.close()
        self.main_thread = False
        self.logger.debug("Background Loop Complete")


if __name__ == "__main__":
    gui = gui()
    gui.main
