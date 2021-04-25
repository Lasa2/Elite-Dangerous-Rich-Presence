import json
import logging
import msvcrt
import os
import re
import time
from queue import Queue
from typing import Dict, Tuple

import win32file
import win32gui

logger = logging.getLogger(__name__)


def getLauncher():
    logger.debug("Searching Window: Elite Dangerous Launcher")
    if win32gui.FindWindow(None, "Elite Dangerous Launcher"):
        return True
    else:
        logger.debug("Elite Dangerous Launcher not found")
        return False


def getGame():
    logger.debug("Searching Window: Elite - Dangerous (CLIENT)")
    if win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)"):
        return True
    else:
        logger.debug("Elite - Dangerous (CLIENT) not found")
        return False


class JournalFileApp:
    active_file: Tuple[int, os.DirEntry] = (0, None)
    queue = Queue()
    running = True
    new_file = False
    stop = False
    last_msg = dict()

    def __init__(self, con, journalpath) -> None:
        self.con = con
        self.journalpath = journalpath

    def get_journal_file(self):
        logger.debug("Scanning for newest journal file")
        with os.scandir(self.journalpath) as it:
            for entry in it:
                if entry.is_file() and "Journal" in entry.name and ".log" in entry.name:
                    date = int(re.sub(r"[a-zA-Z.]", "", entry.name))
                    if date > self.active_file[0]:
                        self.active_file = (date, entry)

    def read_loop(self):
        self.get_journal_file()
        logger.debug("Entering journal loop")
        while getLauncher() and not self.stop:
            if self.last_msg.get("event", None) != "Launcher":
                self.send_message({"event": "Launcher", "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            self.new_file = False
            while self.running and getGame():
                if not self.new_file:
                    self.send_message({"event": "GameStarted", "timestamp": time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                    time.sleep(10)
                self.new_file = False
                handle = win32file.CreateFile(
                    self.active_file[1].path,
                    win32file.GENERIC_READ,
                    win32file.FILE_SHARE_DELETE | win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                detached_handle = handle.Detach()
                file_descriptor = msvcrt.open_osfhandle(
                    detached_handle, os.O_RDONLY)

                with open(file_descriptor, encoding="utf-8") as journal:
                    logger.info("Reading %s", self.active_file[1])
                    while not self.new_file:
                        line = journal.readline()
                        if line == "":
                            time.sleep(0.1)
                        else:
                            event = json.loads(line)
                            ev = event["event"]
                            if ev == "Shutdown":
                                self.new_file = True
                                self.running = False
                            elif ev == "Continued":
                                self.new_file = True
                            self.send_message(event)

                        if self.stop:
                            return

                        self.recv_messages()

                self.get_journal_file()
            self.running = True
            time.sleep(1)
            self.recv_messages()

            if self.stop:
                return
        self.send_message({"event": "GameShutdown", "timestamp": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    def recv_messages(self):
        if self.con.poll():
            msg = self.con.recv()
            if msg == "closed":
                logger.debug("Main application closed, stopping loop")
                self.stop = True

    def send_message(self, msg: Dict):
        self.con.send(msg)
        self.last_msg = msg
