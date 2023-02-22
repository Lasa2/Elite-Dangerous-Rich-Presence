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

from elite_dangerous_rich_presence.settings_config import (
    DEFAULT_JOURNAL_PATH,
    save_afterwards,
    settings,
)


class GeneralOptions(ft.UserControl):
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

        self.journal_path = ft.TextField(
            label="Journal Path",
            value=settings.general.journal_path,
            on_blur=self.validate_journal_path,
            on_submit=self.validate_journal_path,
        )

    @save_afterwards
    async def reset_journal_path(self, event: ft.ControlEvent):
        self.journal_path.value = DEFAULT_JOURNAL_PATH
        await self.journal_path.update_async()

    @save_afterwards
    async def validate_journal_path(self, event: ft.ControlEvent):
        try:
            settings.general.journal_path = event.control.value
        except ValueError as exc:
            event.page.snack_bar = ft.SnackBar(content=ft.Text(exc.errors()[0]["msg"]))  # type: ignore[attr-defined]
            event.page.snack_bar.open = True
            await event.page.update_async()
            await event.control.focus_async()

    @save_afterwards
    async def set_autotray(self, event: ft.ControlEvent):
        settings.general.auto_tray = event.control.value

    @save_afterwards
    async def set_autoclose(self, event: ft.ControlEvent):
        settings.general.auto_close = event.control.value

    @save_afterwards
    async def set_loglevel(self, event: ft.ControlEvent):
        settings.general.log_level = event.control.value

    def build(self):
        return ft.Card(
            content=ft.Container(
                width=600,
                margin=ft.margin.all(10),
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text("General"),
                            trailing=ft.PopupMenuButton(
                                icon=ft.icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Reset Journal Path",
                                        on_click=self.reset_journal_path,
                                    )
                                ],
                            ),
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Switch(
                                    label="Autostart to Tray",
                                    value=settings.general.auto_tray,
                                    on_change=self.set_autotray,
                                ),
                                ft.Switch(
                                    label="Close with Game",
                                    value=settings.general.auto_close,
                                    on_change=self.set_autoclose,
                                ),
                            ],
                        ),
                        self.journal_path,
                        ft.Dropdown(
                            label="Logging Level",
                            options=[
                                ft.dropdown.Option("Debug"),
                                ft.dropdown.Option("Info"),
                                ft.dropdown.Option("Warning"),
                                ft.dropdown.Option("Error"),
                            ],
                            value=settings.general.log_level,
                            on_change=self.set_loglevel,
                        ),
                    ]
                ),
            )
        )
