
from typing import Any, override
import flet as ft

from src.gui.events import DeleteAllSelected
from src.gui.infra.app_bus import AppEventBus, AppState

# TODO: create pagination for this container.
# store all of the created rows, but do not render them yet.
# make it like a sliding window, unload when going out of bounds, and load when in bounds.

# concepts: onscroll event for ListView, list slices, tracking index

class FileCardList(ft.Container):
    content: ft.Control | None
    
    _body: ft.Container
    _list: ft.ListView
    _empty: ft.Container
    _bus: AppEventBus
    def __init__(
        self, 
        bus: AppEventBus,
        row: list[ft.Control],
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
        bus.subscribe(DeleteAllSelected, self.on_delete)

        self._list = ft.ListView(
            scroll=ft.ScrollMode.AUTO,
            controls=row,
            spacing=10,
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
            content=self._empty if len(row) <= 0 else self._list,
            expand=True,
        )

        self.content = self._body
        self._bus = bus

    def on_delete(self, _a: AppState, _b: DeleteAllSelected):
        if len(self._list.controls) <= 0:
            self._body.content = self._empty

    @override
    def will_unmount(self):
        self._bus.unsubscribe(DeleteAllSelected, self.on_delete)
    

