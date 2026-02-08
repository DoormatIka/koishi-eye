
from typing import Any
import flet as ft

from gui.payload_types import Directory
from gui.router.bus import AppEventBus

class FilePicker(ft.Container):
    content: ft.Control | None
    _bus: AppEventBus
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
        bus.subscribe(Directory, lambda s, o: print(s, o))

        btn = ft.Button(
            content="Pick folder",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._g,
            style=ft.ButtonStyle(
                padding=ft.Padding.only(left=20, right=20)
            )
        )
        self.content = btn

    async def _g(self):
        dir_path = await ft.FilePicker().get_directory_path(dialog_title="pick folder to scan")
        await self._bus.notify(Directory(directory=dir_path))

