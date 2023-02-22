import asyncio
from functools import partial

import flet as ft
from loguru import logger

from elite_dangerous_rich_presence.user_controls import (
    EliteDangerousOptions,
    GeneralOptions,
    RichPresenceOptions,
)
from elite_dangerous_rich_presence.util import UiMessages, cancelable


async def close_button(event: ft.ControlEvent):
    await event.page.window_close_async()


async def minimize_button(event: ft.ControlEvent):
    event.page.window_minimized = True
    await event.page.update_async()


async def menu(messages: asyncio.Queue, page: ft.Page):
    page.title = "Elite Dangerous Rich Presence"
    page.window_title_bar_hidden = True
    page.window_frameless = True

    page.window_width = 640
    page.window_min_width = 640
    page.window_max_width = 640

    page.window_height = 850
    page.window_min_height = 850
    page.window_max_height = 850

    await page.window_center_async()

    page.appbar = ft.Card(
        elevation=1.5,
        content=ft.Container(
            width=620,
            content=ft.WindowDragArea(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                "Elite Dangerous Rich Presence",
                                expand=True,
                                style=ft.TextThemeStyle.TITLE_MEDIUM,
                            ),
                            margin=ft.margin.all(10),
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.icons.MINIMIZE,
                            on_click=minimize_button,
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            on_click=close_button,
                        ),
                    ],
                )
            ),
        ),
    )

    await page.add_async(
        GeneralOptions(),
        RichPresenceOptions(),
        EliteDangerousOptions(),
    )

    @cancelable
    async def clock():
        while True:
            msg: UiMessages = await messages.get()  # type: ignore[annotation-unchecked]
            if msg == UiMessages.RESTORE:
                page.window_minimized = False
                await page.update_async()
                await page.window_to_front_async()
            elif msg == UiMessages.EXIT:
                logger.debug("Closing Settings App")
                await page.window_close_async()

    clock_task = asyncio.create_task(clock(), name="clock")

    async def window_event_handler(event: ft.ControlEvent):
        if event.data == "close":
            clock_task.cancel()
            await page.window_destroy_async()

    page.window_prevent_close = True
    page.on_window_event = window_event_handler

    await page.update_async()


class SettingsApp:
    task: asyncio.Task | None = None
    queue: asyncio.Queue = asyncio.Queue()
    open_flag = False

    def open_settings_callback(self):
        self.open_flag = True

    async def launch_settings_app(self):
        logger.debug("Launching Settings App")
        if not self.task or self.task.done():
            settings_app_main = partial(menu, self.queue)
            self.task = asyncio.create_task(
                ft.app_async(settings_app_main),
                name="Settings App",
            )
        else:
            await self.queue.put(UiMessages.RESTORE)


if __name__ == "__main__":
    ft.app(target=partial(menu, asyncio.Queue()))
