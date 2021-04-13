from __future__ import annotations
import json
import os
import re
from typing import Dict, Tuple
import win32gui
import win32file
import msvcrt
from queue import Queue
import asyncio


JOURNALPATH = r"C:\Users\Lasa2\Saved Games\Frontier Developments\Elite Dangerous"


class JournalFileApp:
    active_file: Tuple[int, os.DirEntry] = (0, None)
    queue = Queue()
    running = True
    new_file = False

    def __init__(self) -> None:
        pass

    async def run(self):
        eval_events = asyncio.create_task(self.eval_events())
        await eval_events

        while self.getGame():
            self.get_journal_file()
            read_events = asyncio.create_task(self.read_events())
            await read_events

    def get_journal_file(self):
        with os.scandir(JOURNALPATH) as it:
            for entry in it:
                if entry.is_file() and "Journal" in entry.name and ".log" in entry.name:
                    date = int(re.sub(r"[a-zA-Z.]", "", entry.name))
                    if date > self.active_file[0]:
                        self.active_file = (date, entry)

    async def read_events(self):
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
            while self.running and not self.new_file:
                line = journal.readline()
                if line == "":
                    await asyncio.sleep(0.1)
                else:
                    self.queue.put(json.loads(line))

    async def eval_events(self):
        while self.running:
            if not self.queue.empty():
                event = self.queue.get()
                ev = event["event"]
                if ev == "Shutdown":
                    self.running = False
                elif ev == "Continued":
                    self.new_file = True
            else:
                await asyncio.sleep(0.1)

    def getLauncher(self):
        if win32gui.FindWindow(None, "Elite Dangerous Launcher"):
            return True
        else:
            return False

    def getGame(self):
        if win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)"):
            return True
        else:
            return False


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(JournalFileApp().run())
    # asyncio.run(JournalFileApp().run())
