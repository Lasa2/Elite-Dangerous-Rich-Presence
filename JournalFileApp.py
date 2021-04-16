import json
import msvcrt
import os
import re
import time
from queue import Queue
from typing import Dict, Tuple

import win32file
import win32gui


def getLauncher():
    if win32gui.FindWindow(None, "Elite Dangerous Launcher"):
        return True
    else:
        return False


def getGame():
    if win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)"):
        return True
    else:
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
        with os.scandir(self.journalpath) as it:
            for entry in it:
                if entry.is_file() and "Journal" in entry.name and ".log" in entry.name:
                    date = int(re.sub(r"[a-zA-Z.]", "", entry.name))
                    if date > self.active_file[0]:
                        self.active_file = (date, entry)

    def read_loop(self):
        self.get_journal_file()
        while getLauncher() and not self.stop:
            if self.last_msg.get("event", None) != "Launcher":
                self.send_message({"event": "Launcher", "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            while self.running and getGame():
                self.send_message({"event": "GameStarted", "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
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
                    print(f"Reading {self.active_file[1]}")
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
                self.new_file = False
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
                self.stop = True

    def send_message(self, msg: Dict):
        self.con.send(msg)
        self.last_msg = msg


if __name__ == "__main__":
    JournalFileApp()
