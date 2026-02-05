
from typing import Any
import flet as ft

from gui.router.observer import Observer

class FilePicker(ft.Container):
    content: ft.Control | None
    _observer: Observer
    def __init__(
        self, 
        observer: Observer,
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
        self._observer = observer
        observer.subscribe("directory", lambda e: print(e))

        btn = ft.Button(
            content="Pick folder",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.g,
            style=ft.ButtonStyle(
                padding=ft.Padding.only(left=20, right=20)
            )
        )
        self.content = btn

    async def g(self):
        path = await self.get_dir()
        await self._observer.notify("directory", path)

    async def get_dir(self):
        dir_path = await ft.FilePicker().get_directory_path(dialog_title="pick folder to scan")
        return dir_path

