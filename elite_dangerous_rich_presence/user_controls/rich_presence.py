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

from elite_dangerous_rich_presence.settings_config import save_afterwards, settings


class RichPresenceOptions(ft.UserControl):
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

    @save_afterwards
    async def set_value(self, event: ft.ControlEvent):
        value_name = event.control.label.lower().replace(" ", "_")
        setattr(settings.rich_presence, value_name, event.control.value)

    def build(self):
        return ft.Card(
            content=ft.Container(
                width=600,
                margin=ft.margin.all(10),
                content=ft.Column(
                    [
                        ft.ListTile(title=ft.Text("Rich Presence")),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Container(
                                    content=ft.Switch(
                                        label="CMDR",
                                        value=settings.rich_presence.cmdr,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Power",
                                        value=settings.rich_presence.power,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Location",
                                        value=settings.rich_presence.location,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Container(
                                    content=ft.Switch(
                                        label="Gamemode",
                                        value=settings.rich_presence.gamemode,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Multicrew Mode",
                                        value=settings.rich_presence.multicrew_mode,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Multicrew Size",
                                        value=settings.rich_presence.multicrew_size,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Container(
                                    content=ft.Switch(
                                        label="Time Elapsed",
                                        value=settings.rich_presence.time_elapsed,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Ship Icon",
                                        value=settings.rich_presence.ship_icon,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                                ft.Container(
                                    content=ft.Switch(
                                        label="Ship Text",
                                        value=settings.rich_presence.ship_text,
                                        on_change=self.set_value,
                                    ),
                                    width=200,
                                ),
                            ],
                        ),
                    ]
                ),
            )
        )
