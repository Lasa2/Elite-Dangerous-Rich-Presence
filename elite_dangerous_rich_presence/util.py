import asyncio
import calendar
import time
from enum import Enum, auto, unique
from functools import wraps
from pathlib import Path

from loguru import logger


@unique
class LaunchMode(Enum):
    STEAM = auto()
    EPIC = auto()
    EXECUTABLE = auto()


@unique
class UiMessages(Enum):
    RESTORE = auto()
    EXIT = auto()


def cancelable(func):
    @wraps(func)
    async def cancelled_task(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.debug("Cancelled {func}", func=func)
            return

    return cancelled_task


def now_as_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iso_to_unix(timestamp: str) -> int:
    return calendar.timegm(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))


def remove_old_logs(files: list[str]):
    files.sort(reverse=True)
    for entry in files[3:]:
        Path(entry).unlink()
