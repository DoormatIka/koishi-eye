
from pathlib import Path
from typing import Any
import flet as ft

from gui.payload_types import ImageMatchPayload
from gui.router.observer import AppState, EventBus
from gui.components.card_row import ImageCardRow
from wrappers import clusterer


class FileCardList(ft.Container):
    content: ft.Control | None
    
    _body: ft.Container
    _column: ft.Column
    _empty: ft.Container
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
        bus.subscribe("directory", self.create_matches)

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
        self._body = ft.Container(
            alignment=ft.Alignment.TOP_LEFT,
            content=self._empty,
            expand=True,
        )

        self.content = self._body
        self._bus = bus

    async def create_matches(self, _: AppState, directory: object):
        self._column.controls.clear()

        if isinstance(directory, str):
            image_matches = await clusterer(Path(directory))
            if len(image_matches) <= 0:
                self._body.content = self._empty
            else:
                for pair in image_matches:
                    row = ImageCardRow(self._bus, pair)
                    self._column.controls.append(row)
                self._body.content = self._column

            await self._bus.notify("MATCHES", ImageMatchPayload(total=len(image_matches)))

        self.update()

