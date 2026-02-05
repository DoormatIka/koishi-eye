
from collections.abc import Collection
from typing import Any
import flet as ft

from hashers.types import CombinedImageHash
from gui.models.image import ModelImage

class ImageCardRow(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    def __init__(
        self, 
        images: Collection[CombinedImageHash],
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

        containers = self.create_model_images(images)

        img_row = ft.Row(
            controls=containers,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

        self.width = float("inf")
        self.content = img_row
        self.padding = 10
        self.border_radius = 5
        self.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREY_300)

    def create_model_images(self, matched_images: Collection[CombinedImageHash]) -> list[ft.Control]:
        containers: list[ft.Control] = []

        for img in matched_images:
            model = ModelImage(hash=img)
            container = ft.Container(
                content=ft.Image(
                    src=str(img.path),
                    height=150,
                    fit=ft.BoxFit.COVER,
                    expand=1,
                ),
                on_click=lambda ev: self.toggle_delete(ev, model)
            )
            containers.append(container)

        return containers

    def toggle_delete(self, e: ft.Event[ft.Container], model: ModelImage):
        is_deleted = model.toggle_delete()
        if is_deleted:
            e.control.border = ft.border.all(2, ft.Colors.RED)
        else:
            e.control.border = None

        e.control.update()

