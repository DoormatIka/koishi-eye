
import flet as ft

from typing import Any

from src.gui.components.upper_row.image_counter import ImageCounter
from src.gui.components.upper_row.logs import Logs
from src.gui.infra.app_bus import AppEventBus
from src.gui.infra.logger import Logger

class UpperBar(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _image_count: ImageCounter
    _logs: Logs
    _bus: AppEventBus
    def __init__(
        self, 
        bus: AppEventBus,
        logger: Logger,
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
        self._logs = Logs(bus, logger)

        self.content = ft.Row(
            controls=[self._image_count, self._logs]
        )
        self._bus = bus

    
