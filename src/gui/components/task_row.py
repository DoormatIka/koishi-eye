
import flet as ft

from typing import Any

from gui.components.delete import DeleteButton
from gui.router.bus import AppEventBus
from gui.components.file_picker import FilePicker

class TaskRow(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

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
        self._bus = bus

        file_picker = FilePicker(bus=bus)
        delete_button = DeleteButton(bus=bus)

        self.content = ft.Row(
            controls=[file_picker, delete_button]
        )
