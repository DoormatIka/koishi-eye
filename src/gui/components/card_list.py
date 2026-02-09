
from pathlib import Path
from typing import Any
import flet as ft

from gui.events import Directory, ImageUpdate
from gui.infra.app_bus import AppState, AppEventBus
from gui.components.card_row import ImageCardRow
from wrappers import clusterer



class FileCardList(ft.Container):
    content: ft.Control | None
    
    _body: ft.Container
    _column: ft.Column
    _empty: ft.Container
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
        bus.subscribe(Directory, self.create_matches)

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

    async def create_matches(self, state: AppState, obj: Directory):
        self._column.controls.clear()
        if obj.directory is None:
            raise ValueError("Directory is null!")

        print(f"create_matches: {obj}")
        image_matches = await state.finder.create_hashes_from_directory(Path(obj.directory))
        similar_images = state.finder.get_similar_objects(image_matches)
        if len(image_matches) <= 0:
            self._body.content = self._empty
        else:
            for pair in similar_images:
                row = ImageCardRow(self._bus, pair)
                self._column.controls.append(row)
            self._body.content = self._column

        await self._bus.notify(ImageUpdate(total=len(image_matches)))

        self.update()

