import asyncio
import calendar
import time
from enum import Enum, auto, unique
from functools import wraps
from pathlib import Path

import httpx
from loguru import logger

from elite_dangerous_rich_presence import API_LATEST_RELEASE_URL, __version_info__


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


def is_latest_version() -> bool:
    response = httpx.get(
        API_LATEST_RELEASE_URL,
        headers={
            "Accept": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    tag_name = response.json().get("tag_name", "V0.0")
    logger.debug("Checking version, latest tag: {tag_name}", tag_name=tag_name)
    try:
        latest_major, latest_minor = tag_name[1:].split(".")
        latest_major, latest_minor = int(latest_major), int(latest_minor)
    except ValueError:
        logger.warning(
            "Unable to parse latest release version! Skipping version check."
        )
        return True
    current_major, current_minor = __version_info__

    if (
        latest_major > current_major
        or latest_major == current_major
        and latest_minor > current_minor
    ):
        return False
    return True
