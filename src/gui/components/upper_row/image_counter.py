
import flet as ft

from typing import Any

from gui.events import DeleteAllSelected, ImageUpdate
from gui.infra.bus import AppState, AppEventBus

class ImageCounter(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _image_count: ft.Text
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
        bus.subscribe(ImageUpdate, self.on_image_update)
        bus.subscribe(DeleteAllSelected, self.on_delete_selected)
        self._image_count = ft.Text(
            value=""
        )

        self._bus = bus
        self.content = self._image_count

    def on_image_update(self, _: AppState, payload: ImageUpdate):
        self._image_count.value = f"Duplicate images: {payload.total}"
        
    def on_delete_selected(self, state: AppState, _: DeleteAllSelected):
        self._image_count.value = f"Duplicate images: {state.total_images}"

