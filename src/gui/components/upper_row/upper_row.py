
import flet as ft

from typing import Any

from gui.components.upper_row.image_counter import ImageCounter
from gui.router.bus import AppEventBus

class UpperBar(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _image_count: ImageCounter
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

        self._image_count = ImageCounter(bus=bus)
        # add logger here.


        self.content = ft.Row(
            controls=[self._image_count]
        )
        self._bus = bus

    
