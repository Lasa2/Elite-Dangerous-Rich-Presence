import asyncio
import os
from pathlib import Path

import win32gui
from loguru import logger
from pypresence import AioPresence

from elite_dangerous_rich_presence import LATEST_RELEASE_URL, __version__
from elite_dangerous_rich_presence.event_processor import EventProcessor
from elite_dangerous_rich_presence.journal_reader import (
    JournalReader,
    any_active,
    game_active,
    launcher_active,
)
from elite_dangerous_rich_presence.settings_app import SettingsApp
from elite_dangerous_rich_presence.settings_config import settings
from elite_dangerous_rich_presence.taskbar_app import TaskbarApp
from elite_dangerous_rich_presence.user_controls.elite_dangerous import (
    launch_elite_dangerous,
)
from elite_dangerous_rich_presence.util import (
    UiMessages,
    is_latest_version,
    remove_old_logs,
)


def file_log_filter(record):
    level_no = logger.level(settings.general.log_level.upper()).no
    return record["level"].no >= level_no


logger.add(
    Path("edrp-{time}.log"),
    filter=file_log_filter,
    level="DEBUG",
    diagnose=False,
    retention=remove_old_logs,
)


@logger.catch
async def main():
    logger.info(
        "Elite Dangerous Rich Presence - Version {version}",
        version=__version__,
    )
    logger.debug("Loaded Settings: {settings}", settings=settings.json())

    settings_app = SettingsApp()

    taskbar_app = TaskbarApp(
        f"Elite Dangerous Rich Presence - V{__version__}",
        icon_path="elite-dangerous-clean.ico",
        callback=settings_app.open_settings_callback,
    )

    if settings.general.check_updates and not is_latest_version():
        taskbar_app.show_toast(
            "A new version is available! Click here to open in browser.",
            lambda: os.startfile(LATEST_RELEASE_URL),
        )

    presence = AioPresence(535809971867222036)
    logger.debug("Connecting Rich Presence")
    await presence.connect()

    if not settings.general.auto_tray:
        await settings_app.launch_settings_app()

    if settings.elite_dangerous.auto_launch and not any_active():
        logger.debug("Launching Elite Dangerous")
        launch_elite_dangerous()

    if settings.general.auto_close:
        # Dont close immediately if auto close is on,
        # instead wait until the game or launcher appeared at least once
        while not any_active():
            if settings_app.open_flag:
                settings_app.open_flag = False
                await settings_app.launch_settings_app()

            # Close if taskbar app is closed
            if win32gui.PumpWaitingMessages() != 0:
                await settings_app.queue.put(UiMessages.EXIT)
                if settings_app.task:
                    await asyncio.wait_for(settings_app.task, None)
                # Can't call presence.close(), because loop isn't closed yet
                presence.send_data(2, {"v": 1, "client_id": presence.client_id})
                presence.sock_writer.close()
                await logger.complete()
                logger.stop()
                return

            await asyncio.sleep(0.1)

    event_queue = asyncio.Queue()
    journal_reader = JournalReader(event_queue)
    journal_task = asyncio.create_task(journal_reader.watch())

    event_processor = EventProcessor()

    active = True
    while active:
        if settings_app.open_flag:
            settings_app.open_flag = False
            await settings_app.launch_settings_app()

        # Returns non-zero if taskbar app is closed
        if win32gui.PumpWaitingMessages() != 0:
            active = False

        if settings.general.auto_close and not (launcher_active() or game_active()):
            active = False

        while not event_queue.empty():
            event = await event_queue.get()
            await event_processor(event)
            await presence.update(**event_processor.rpc_dict())

            if event["event"] == "LauncherClosed" or event["event"] == "Shutdown":
                await presence.clear()

            # Remove identfiying information from logs
            if "FID" in event:
                event["FID"] = "XXXXX"
            logger.debug(event)

            event_queue.task_done()

        await asyncio.sleep(0.1)

    # Can't call presence.close(), because loop isn't closed yet
    presence.send_data(2, {"v": 1, "client_id": presence.client_id})
    presence.sock_writer.close()

    journal_task.cancel()
    await asyncio.wait_for(journal_task, None)

    if settings_app.task:
        await settings_app.queue.put(UiMessages.EXIT)
        await asyncio.wait_for(settings_app.task, None)

    await logger.complete()
    logger.stop()


asyncio.run(main())
