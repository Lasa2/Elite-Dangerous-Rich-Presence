import asyncio
import json
import msvcrt
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import win32api
import win32file
import win32gui
import win32process
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


def get_creation_time():
    hwnd = win32gui.FindWindow(None, "Elite - Dangerous (CLIENT)")
    _, process_id = win32process.GetWindowThreadProcessId(hwnd)
    process_handle = win32api.OpenProcess(5120, False, process_id)
    process_times = win32process.GetProcessTimes(process_handle)

    return process_times["CreationTime"]


def now_with_timezone():
    return datetime.now(timezone.utc).astimezone()


def local_timezone():
    return now_with_timezone().tzinfo


@dataclass
class JournalFile:
    path: Path
    timestamp: datetime
    part: int


class JournalReader:
    file = JournalFile(Path("."), datetime(1, 1, 1, 1, 1, 1, tzinfo=local_timezone()), 0)
    queue: asyncio.Queue

    def __init__(self, queue: asyncio.Queue) -> None:
        self.queue = queue

    async def get_journal_file(self):
        while True:
            for entry in settings.general.journal_path.glob("*Journal*.log"):
                if not entry.is_file():
                    continue
                logger.debug("Found Entry: {entry}", entry=entry)

                if (
                    # New Format: Journal.YYYY-MM-DDThhmmss.part.log
                    match := re.search(r"(\d{4}-\d{2}-\d{2}T\d{6}).(\d{2})", entry.name)
                    # Old Format: Journal.YYMMDDhhmmss.part.log
                ) or (
                    match := re.search(r"(\d{2}\d{2}\d{2}\d{6}).(\d{2})", entry.name)
                ):
                    timestamp, part = match.groups()
                    timestamp += time.strftime("%z")

                    if "T" in timestamp:
                        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H%M%S%z")
                    else:
                        timestamp = datetime.strptime(timestamp, "%y%m%d%H%M%S%z")
                    logger.debug(
                        "Found Date: {date}, Part: {part}", date=timestamp, part=part
                    )

                    if timestamp > self.file.timestamp and entry != self.file.path:
                        self.file = JournalFile(entry, timestamp, part)

            if self.file.timestamp < get_creation_time():
                logger.debug("Files are older than launcher timestamp, ignoring file")
                await asyncio.sleep(10)
            else:
                return

    async def read(self):
        handle = win32file.CreateFile(
            str(self.file.path),
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

        logger.debug("Reading {file}", file=self.file.path)
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
                while game_active():
                    await asyncio.sleep(1)
            elif launcher_active():
                logger.debug("Launcher open, waiting for Elite or Launcher close")
                await self.queue.put({"event": "Launcher", "timestamp": now_as_iso()})
                while not game_active() and launcher_active():
                    await asyncio.sleep(1)

                if launcher_active():
                    logger.debug("Elite open")
                else:
                    logger.debug("Launcher closed")
                    await self.queue.put(
                        {
                            "event": "LauncherClosed",
                            "timestamp": now_as_iso(),
                        }
                    )
            else:
                await asyncio.sleep(1)
