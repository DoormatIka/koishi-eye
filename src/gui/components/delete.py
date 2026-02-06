
from typing import Any
import flet as ft

from gui.router.observer import EventBus

class DeleteButton(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _bus: EventBus
    def __init__(
        self, 
        bus: EventBus,
        width: float | None = None,
        height: float | None = None,
        expand: bool | None = None,
        **kwargs: Any # pyright: ignore[reportAny, reportExplicitAny]
    ):
        super().__init__(
            width=width, 
            height=height,
            expand=expand,
            **kwargs # pyright: ignore[reportAny]
        )
        self._bus = bus

        btn = ft.Button(
            content="Delete all selected",
            icon=ft.Icons.DELETE_FOREVER,
            on_click=self.delete_selected,
            style=ft.ButtonStyle(
                padding=ft.Padding.only(left=20, right=20)
            )
        )
        self.content = btn

    async def delete_selected(self):
        await self._bus.notify("DELETE_SEL_IMG", None)



