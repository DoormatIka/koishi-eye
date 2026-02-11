
from typing import Any
import flet as ft

from src.gui.events import Directory, ImageUpdate, SevereAppError, UIEvent
from src.gui.infra.app_bus import AppEventBus, AppState

class FilePicker(ft.Container):
    content: ft.Control | None
    _bus: AppEventBus
    _btn: ft.Button
    def __init__(
        self, 
        bus: AppEventBus,
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
        bus.subscribe(ImageUpdate, self.unlock_button)
        bus.subscribe(SevereAppError, self.unlock_button)

        self._btn = ft.Button(
            content="Pick folder",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._g,
            style=ft.ButtonStyle(
                padding=ft.Padding.only(left=20, right=20)
            ),
            disabled=False
        )
        self.content = self._btn

    def unlock_button(self, _a: AppState, _b: UIEvent):
        self._btn.disabled = False
        self.update()

    async def _g(self):
        dir_path = await ft.FilePicker().get_directory_path(dialog_title="pick folder to scan")
        if dir_path is None:
            return

        self._btn.disabled = True
        await self._bus.notify(Directory(directory=dir_path))

