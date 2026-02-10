
from pathlib import Path
from typing import Any
import flet as ft

from src.gui.events import Directory, ImageUpdate
from src.gui.infra.app_bus import AppState, AppEventBus
from src.gui.components.card_row import ImageCardRow

# TODO: create pagination for this container.
# store all of the created rows, but do not render them yet.
# make it like a sliding window, unload when going out of bounds, and load when in bounds.

# concepts: onscroll event for ListView, list slices, tracking index

# calculate the amount of items that can fit into the screen (variable)
# and add 5 more items on each side of the bound.

class FileCardList(ft.Container):
    content: ft.Control | None
    
    _body: ft.Container
    _list: ft.ListView
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

        self._list = ft.ListView(
            scroll=ft.ScrollMode.AUTO,
            controls=[],
            spacing=10,
            item_extent=180
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
        self._list.controls.clear()

        if obj.directory is None:
            raise ValueError("Directory is null!")

        image_hashes = await state.finder.create_hashes_from_directory(Path(obj.directory))
        similar_images = state.finder.get_similar_objects(image_hashes)
        if len(similar_images) <= 0:
            self._body.content = self._empty
        else:
            for pair in similar_images:
                row = ImageCardRow(self._bus, pair)
                self._list.controls.append(row)
            self._body.content = self._list

        await self._bus.notify(ImageUpdate(total=len(similar_images)))

        self.update()

