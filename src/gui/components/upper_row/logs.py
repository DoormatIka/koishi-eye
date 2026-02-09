
import flet as ft

from typing import Any

from src.gui.infra.app_bus import AppEventBus
from src.gui.infra.logger import Logger, Progress, Info

class Logs(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _progress: ft.Text
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
        logger.subscribe(Progress, self._on_progress)
        logger.subscribe(Info, self._on_info)

        self._progress = ft.Text(value="")
        self.content = self._progress
        self._bus = bus

    def _on_info(self, _: None, payload: Info):
        self._progress.value = f"INFO: {payload.msg}"

    def _on_progress(self, _: None, payload: Progress):
        filename = truncate_name(payload.path.name)
        is_complete = payload.is_complete
        if is_complete:
            self._progress.value = f"Completed! Scanned {payload.current} images."
        else:
            self._progress.value = f"Scanned ({payload.current}): {filename}"

        self.update()


def truncate_name(name: str):
    max_length = 20
    if len(name) > max_length:
        return name[:max_length] + "..."
    return name
