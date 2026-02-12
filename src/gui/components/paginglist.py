
import os
from pathlib import Path
from typing import Any, Literal, cast
import flet as ft

from src.finders import ImagePair
from src.gui.components.card_row import ImageCardRow
from src.gui.events import DeleteAllSelected, Directory, ImageUpdate
from src.gui.components.card_list import FileCardList
from src.gui.infra.app_bus import AppEventBus, AppState
from src.hashers import CombinedImageHash

class PagingList(ft.Container):
    content: ft.Control | None
    expand: bool | int | None

    _bus: AppEventBus

    _similar_images: set[ImagePair]
    _selected_images: set[CombinedImageHash]
    _pages: list[list[ft.Control]]
    _list_view: ft.Container
    _left: ft.IconButton
    _right: ft.IconButton
    _page_number: ft.Text

    _page_size: int
    _current_page: int
    def __init__(
        self, 
        bus: AppEventBus,
        page_size: int = 10,
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
        bus.subscribe(DeleteAllSelected, self.delete_rows)

        self._bus = bus
        self._current_page = 0
        self._pages = []
        self._page_size = page_size
        self._similar_images = set()
        self._selected_images = set()

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
        self._page_number = ft.Text(value=f"{self._current_page}/{len(self._pages)}")
        row = ft.Row(
            controls=[self._left, self._page_number, self._right],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content = ft.Column(
            controls=[self._list_view, row]
        )
        self.expand = expand

    def move_left(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.update_page()

    def move_right(self):
        if self._current_page < len(self._pages) - 1:
            self._current_page += 1
            self.update_page()

    def update_page(self):
        """
        Calculate the pages for each change to a page.
        """
        self.update_page_number()
        if len(self._pages) <= 0:
            self._list_view.content = FileCardList(self._bus, [])
        else:
            self._list_view.content = FileCardList(self._bus, self._pages[self._current_page])

        self.update()

    def update_page_number(self):
        visual_current_page = 0
        if len(self._pages) > 0:
            visual_current_page = self._current_page + 1
        else:
            visual_current_page = 0

        self._page_number.value = f"{visual_current_page}/{len(self._pages)}"

    def delete_files(self):
        for img in self._selected_images:
            if os.path.isfile(img.path):
                # print(f"deleted: {img.path}")
                try:
                    os.remove(img.path)
                except (Exception):
                    pass

    async def delete_rows(self, _a: AppState, _b: DeleteAllSelected):
        self._similar_images = {
            pair for pair in self._similar_images
            if pair[0] not in self._selected_images 
            and pair[1] not in self._selected_images
        }

        self.delete_files()
        await self.paginate_images()

        if self._current_page >= len(self._pages) and self._current_page > 0:
            self._current_page -= 1

        self._selected_images.clear()

        self.update_page()

    async def paginate_images(self):
        self._pages.clear()

        ordered_items = sorted(self._similar_images, key=lambda x: x[0].path)
        for i in range(0, len(ordered_items), self._page_size):
            chunk = ordered_items[i : i + self._page_size]
            page_controls = [ImageCardRow(pair, on_select=self.handle_selection, selected_hashes=self._selected_images) for pair in chunk]
            self._pages.append(cast(list[ft.Control], page_controls))

        await self._bus.notify(ImageUpdate(total=len(self._similar_images)))

    def handle_selection(self, img: CombinedImageHash, is_selected: Literal["add", "remove"]):
        if is_selected == "add":
            self._selected_images.add(img)
        if is_selected == "remove":
            self._selected_images.discard(img)
        
        print(len(self._selected_images))
        self.update()

    async def create_matches(self, state: AppState, obj: Directory):
        self._similar_images.clear()
        self._selected_images.clear()

        if obj.directory is None:
            raise ValueError("Directory is null!")

        image_hashes = await state.finder.create_hashes_from_directory(Path(obj.directory))
        self._similar_images = state.finder.get_similar_objects(image_hashes)

        await self.paginate_images()
        self.update_page()
        

