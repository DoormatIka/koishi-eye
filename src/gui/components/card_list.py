
from pathlib import Path
from typing import Any
import flet as ft

from gui.router.observer import AppState, Observer
from gui.components.card_row import ImageCardRow
from wrappers import clusterer


class FileCardList(ft.Container):
    content: ft.Control | None
    
    _body: ft.Container
    _image_count: ft.Text
    _column: ft.Column
    _empty: ft.Container
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
        observer.subscribe("directory", self.create_matches)

        self._column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[]
        )
        self._empty = ft.Container(
            content=ft.Text(
                text_align=ft.TextAlign.CENTER,
                value="No images found!",
            ),
            alignment=ft.Alignment.CENTER,
            expand=True
        )
        self._image_count = ft.Text(
            value=""
        )
        status = ft.Row(controls=[self._image_count])
        
        self._body = ft.Container(
            alignment=ft.Alignment.TOP_LEFT,
            content=self._empty,
            expand=True,
        )
        self.content = ft.Column(
            controls=[status, self._body],
            expand=True
        )
        self._observer = observer

    async def create_matches(self, _: AppState, directory: object):
        self._column.controls.clear()

        if isinstance(directory, str):
            image_matches = await clusterer(Path(directory))
            if len(image_matches) <= 0:
                self._body.content = self._empty
                self._image_count.value = ""
            else:
                for pair in image_matches:
                    row = ImageCardRow(self._observer, pair)
                    self._column.controls.append(row)
                self._body.content = self._column

            self._image_count.value = f"Duplicate images: {len(image_matches)}"

        self.update()

