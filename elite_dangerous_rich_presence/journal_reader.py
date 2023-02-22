import asyncio
import json
import msvcrt
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import win32file
import win32gui
from loguru import logger

from elite_dangerous_rich_presence.settings_config import settings
from elite_dangerous_rich_presence.util import cancelable, now_as_iso


def launcher_active():
    if win32gui.FindWindow(None, "Elite Dangerous Launcher"):
        return True
    else:
        return False


def game_active():
    if win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)"):
        return True
    else:
        return False


def any_active():
    return launcher_active() or game_active()


@dataclass
class JournalFile:
    path: Path
    timestamp: datetime
    part: int


class JournalReader:
    current_file = JournalFile(Path("."), datetime(1, 1, 1, 1, 1, 1), 0)
    last_file = JournalFile(Path("."), datetime(1, 1, 1, 1, 1, 1), 0)
    queue: asyncio.Queue

    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue

    async def get_journal_file(self):
        for entry in settings.general.journal_path.glob("*Journal*.log"):
            if not entry.is_file():
                continue
            logger.debug("Found Entry: {entry}", entry=entry)

            if (
                # New Format: Journal.YYYY-MM-DDThhmmss.part.log
                match := re.search(r"(\d{4}-\d{2}-\d{2}T\d{6}).(\d{2})", entry.name)
                # Old Format: Journal.YYMMDDhhmmss.part.log
            ) or (match := re.search(r"(\d{2}\d{2}\d{2}\d{6}).(\d{2})", entry.name)):
                timestamp, part = match.groups()

                if "T" in timestamp:
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H%M%S")
                else:
                    timestamp = datetime.strptime(timestamp, "%y%m%d%H%M%S")
                logger.debug(
                    "Found Date: {date}, Part: {part}", date=timestamp, part=part
                )

                if timestamp > self.current_file.timestamp:
                    self.last_file = self.current_file
                    self.current_file = JournalFile(entry, timestamp, part)

                elif entry == self.last_file.path:
                    logger.debug("No new file found, now waiting")
                    await asyncio.sleep(10)

    async def read(self):
        handle = win32file.CreateFile(
            str(self.current_file.path),
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

        logger.debug("Reading {file}", file=self.current_file.path)
        with open(file_descriptor, encoding="utf-8") as journal:
            while True:
                if line := journal.readline():
                    event = json.loads(line)
                    await self.queue.put(event)
                    if event["event"] == "Shutdown" or event["event"] == "Continued":
                        return
                else:
                    await asyncio.sleep(0.1)

    @cancelable
    async def watch(self):
        logger.debug("Waiting for Elite or Launcher")
        while True:
            if game_active():
                logger.debug("Elite open")
                await self.get_journal_file()
                await self.read()
                await self.queue.join()
            elif launcher_active():
                logger.debug("Launcher open, waiting for Elite or Launcher close")
                await self.queue.put({"event": "Launcher", "timestamp": now_as_iso()})
                while not game_active() and launcher_active():
                    await asyncio.sleep(1)
                logger.debug("Elite open or Launcher closed")
                await self.queue.put(
                    {
                        "event": "LauncherClosed",
                        "timestamp": now_as_iso(),
                    }
                )
            else:
                await asyncio.sleep(1)