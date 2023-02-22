import os
import subprocess
from typing import Any

import flet as ft
from flet_core.types import (
    AnimationValue,
    ClipBehavior,
    OffsetValue,
    ResponsiveNumber,
    RotateValue,
    ScaleValue,
)
from loguru import logger

from elite_dangerous_rich_presence.settings_config import (
    LaunchMode,
    save_afterwards,
    settings,
)


def get_launch_url() -> str:
    return {
        LaunchMode.STEAM: f"{settings.elite_dangerous.path}//{settings.elite_dangerous.arguments}",
        LaunchMode.EPIC: str(settings.elite_dangerous.path),
        LaunchMode.EXECUTABLE: f"{settings.elite_dangerous.path} {settings.elite_dangerous.arguments}",
    }[settings.elite_dangerous.launch_mode]


def launch_elite_dangerous(*_):
    url = get_launch_url()
    if not url.strip():
        logger.debug("Empty url")
        return

    # Each launch_mode needs a different way to launch detatched
    if settings.elite_dangerous.launch_mode is LaunchMode.EXECUTABLE:
        logger.debug("Launching executable: {cmd}", cmd=url)
        subprocess.Popen(
            url,
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_BREAKAWAY_FROM_JOB,
        )
    elif settings.elite_dangerous.launch_mode is LaunchMode.STEAM:
        logger.debug("Launching via Steam: {url}", url=url)
        subprocess.Popen(f"explorer.exe {url}")
    elif settings.elite_dangerous.launch_mode is LaunchMode.EPIC:
        logger.debug("Launching via Epic: {url}", url=url)
        os.startfile(url)


class EliteDangerousOptions(ft.UserControl):
    def __init__(
        self,
        controls: list[ft.Control] | None = None,
        ref: ft.Ref | None = None,
        width: ft.OptionalNumber = None,
        height: ft.OptionalNumber = None,
        left: ft.OptionalNumber = None,
        top: ft.OptionalNumber = None,
        right: ft.OptionalNumber = None,
        bottom: ft.OptionalNumber = None,
        expand: None | bool | int = None,
        col: ResponsiveNumber | None = None,
        opacity: ft.OptionalNumber = None,
        rotate: RotateValue = None,
        scale: ScaleValue = None,
        offset: OffsetValue = None,
        aspect_ratio: ft.OptionalNumber = None,
        animate_opacity: AnimationValue = None,
        animate_size: AnimationValue = None,
        animate_position: AnimationValue = None,
        animate_rotation: AnimationValue = None,
        animate_scale: AnimationValue = None,
        animate_offset: AnimationValue = None,
        on_animation_end=None,
        visible: bool | None = None,
        disabled: bool | None = None,
        data: Any = None,
        clip_behavior: ClipBehavior | None = None,
    ):
        super().__init__(
            controls,
            ref,
            width,
            height,
            left,
            top,
            right,
            bottom,
            expand,
            col,
            opacity,
            rotate,
            scale,
            offset,
            aspect_ratio,
            animate_opacity,
            animate_size,
            animate_position,
            animate_rotation,
            animate_scale,
            animate_offset,
            on_animation_end,
            visible,
            disabled,
            data,
            clip_behavior,
        )

        self.elite_path_field = ft.TextField(
            label="Elite Dangerous Path",
            value=settings.elite_dangerous.path,
            on_submit=self.validate_elite_path,
            on_blur=self.validate_elite_path,
            disabled=(
                False
                if settings.elite_dangerous.launch_mode is LaunchMode.EXECUTABLE
                else True
            ),
        )
        self.arguments_field = ft.TextField(
            label="Arguments",
            value=settings.elite_dangerous.arguments,
            on_submit=self.set_arguments,
            on_blur=self.set_arguments,
            disabled=(
                True
                if settings.elite_dangerous.launch_mode is LaunchMode.EPIC
                else False
            ),
        )

    @save_afterwards
    async def set_arguments(self, event: ft.ControlEvent):
        settings.elite_dangerous.arguments = event.control.value

    @save_afterwards
    async def set_auto_launch(self, event: ft.ControlEvent):
        settings.elite_dangerous.auto_launch = event.control.value

    @save_afterwards
    async def set_steam(self, event: ft.ControlEvent):
        settings.elite_dangerous.launch_mode = LaunchMode.STEAM
        self.elite_path_field.value = "steam://run/359320"
        self.elite_path_field.disabled = True
        self.arguments_field.disabled = False

        settings.elite_dangerous.path = self.elite_path_field.value
        await self.update_async()

    @save_afterwards
    async def set_epic_games(self, event: ft.ControlEvent):
        settings.elite_dangerous.launch_mode = LaunchMode.EPIC
        self.elite_path_field.value = "com.epicgames.launcher://apps/9c203b6ed35846e8a4a9ff1e314f6593?action=launch&silent=true"
        self.elite_path_field.disabled = True
        self.arguments_field.disabled = True

        settings.elite_dangerous.path = self.elite_path_field.value
        await self.update_async()

    @save_afterwards
    async def set_executable(self, event: ft.ControlEvent):
        settings.elite_dangerous.launch_mode = LaunchMode.EXECUTABLE
        self.elite_path_field.value = ""
        self.elite_path_field.disabled = False
        self.arguments_field.disabled = False

        settings.elite_dangerous.path = self.elite_path_field.value
        await self.update_async()

    @save_afterwards
    async def validate_elite_path(self, event: ft.ControlEvent):
        if settings.elite_dangerous.launch_mode is LaunchMode.EXECUTABLE:
            try:
                settings.elite_dangerous.path = self.elite_path_field.value
            except ValueError as exc:
                event.page.snack_bar = ft.SnackBar(
                    content=ft.Text(exc.errors()[0]["msg"])  # type: ignore[attr-defined]
                )
                event.page.snack_bar.open = True
                await event.page.update_async()
                await event.control.focus_async()

    def build(self):
        return ft.Card(
            content=ft.Container(
                width=600,
                margin=ft.margin.all(10),
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            title=ft.Text("Elite Dangerous"),
                            on_long_press=launch_elite_dangerous,
                            trailing=ft.PopupMenuButton(
                                icon=ft.icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Steam", on_click=self.set_steam
                                    ),
                                    ft.PopupMenuItem(
                                        text="Epic Games", on_click=self.set_epic_games
                                    ),
                                    ft.PopupMenuItem(
                                        text="Executable", on_click=self.set_executable
                                    ),
                                ],
                            ),
                        ),
                        self.elite_path_field,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Switch(
                                    label="Autostart Game",
                                    value=settings.elite_dangerous.auto_launch,
                                    on_change=self.set_auto_launch,
                                ),
                                self.arguments_field,
                            ],
                        ),
                    ]
                ),
            )
        )
