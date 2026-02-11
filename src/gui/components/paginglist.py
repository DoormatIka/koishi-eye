
from pathlib import Path
from typing import Any
import flet as ft

from src.gui.components.card_row import ImageCardRow
from src.gui.events import DeleteAllSelected, Directory, ImageUpdate
from src.gui.components.card_list import FileCardList
from src.gui.infra.app_bus import AppEventBus, AppState

class PagingList(ft.Container):
    content: ft.Control | None
    expand: bool | int | None

    _bus: AppEventBus
    _total_list: list[ft.Control]
    _list_view: ft.Container
    _left: ft.IconButton
    _right: ft.IconButton
    _page_number: ft.Text

    _current_page: int
    _total_page: int
    def __init__(
        self, 
        bus: AppEventBus,
        width: float | None = None,
        height: float | None = None,
        expand: bool | int | None = None,
        **kwargs: Any # pyright: ignore[reportAny, reportExplicitAny]
    ):
        super().__init__(
            width=width, 
            height=height,
            expand=expand,
            **kwargs # pyright: ignore[reportAny]
        )
        bus.subscribe(Directory, self.create_matches)
        bus.subscribe(DeleteAllSelected, self.refresh_lists)

        self._bus = bus
        self._current_page = 1
        self._total_page = 10
        self._total_list = []
        self._list_view = ft.Container(
            expand=True,
            border=ft.Border.all(width=0.1, color=ft.Colors.WHITE),
            padding=ft.Padding.all(5)
        )
        self._left = ft.IconButton(
            icon=ft.Icons.ARROW_CIRCLE_LEFT,
            on_click=self.move_left,
            icon_size=30,
        )
        self._right = ft.IconButton(
            icon=ft.Icons.ARROW_CIRCLE_RIGHT,
            on_click=self.move_right,
            icon_size=30,
        )
        self._page_number = ft.Text(value=f"{self._current_page}/{self._total_page}")
        row = ft.Row(
            controls=[self._left, self._page_number, self._right],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content = ft.Column(
            controls=[self._list_view, row]
        )
        self.expand = expand

    def move_left(self):
        if self._current_page > 1:
            self._current_page -= 1
            self.update_page()

    def move_right(self):
        if self._current_page < self._total_page:
            self._current_page += 1
            self.update_page()

    def update_page(self):
        self._page_number.value = f"{self._current_page}/{self._total_page}"

    def refresh_lists(self, _a: AppState, _b: DeleteAllSelected):
        """
        Recalculate the pages for each change to a page.
        """
        pass
    def slice_to_chunks(self):
        pass

    async def create_matches(self, state: AppState, obj: Directory):
        self._total_list.clear()

        if obj.directory is None:
            raise ValueError("Directory is null!")

        image_hashes = await state.finder.create_hashes_from_directory(Path(obj.directory))
        similar_images = state.finder.get_similar_objects(image_hashes)
        for pair in similar_images:
            row = ImageCardRow(self._bus, pair)
            self._total_list.append(row)

        await self._bus.notify(ImageUpdate(total=len(similar_images)))

        self._list_view.content = FileCardList(self._bus, self._total_list)
        self.update()

