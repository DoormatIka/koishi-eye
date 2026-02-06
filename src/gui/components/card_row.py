
from collections.abc import Collection
from dataclasses import dataclass
from typing import Any, cast
import flet as ft

from gui.router.observer import EventBus
from hashers.types import CombinedImageHash
from gui.models.image import ModelImage

@dataclass
class ImageView:
    container: ft.Container
    icon: ft.Icon

class ImageCardRow(ft.Container):
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _observer: EventBus
    _views: list[ImageView]
    _selected_image: int | None
    def __init__(
        self, 
        observer: EventBus,
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
        self._observer = observer
        views = self.create_model_images(images)

        img_row = ft.Row(
            controls=[view.container for view in views],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

        self.width = float("inf")
        self.content = img_row
        self.padding = 10
        self.border_radius = 5
        self.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREY_300)

        self._views = views
        self._selected_image = None

    def create_model_images(self, matched_images: Collection[CombinedImageHash]) -> list[ImageView]:
        containers: list[ImageView] = []

        for i, img in enumerate(matched_images):
            imgui = ft.Image(
                src=str(img.path),
                height=150,
                fit=ft.BoxFit.COVER,
            )
            icon = ft.Icon(
                ft.Icons.CHECK_CIRCLE,
                visible=False,
                size=24,
                color=ft.Colors.WHITE,
                right=8,
                top=8,
                shadows=[
                    ft.BoxShadow(
                        spread_radius=20,
                        blur_radius=7,
                        color=ft.Colors.BLACK
                    )
                ]
            )
            stack = ft.Stack(controls=[imgui, icon], clip_behavior=ft.ClipBehavior.HARD_EDGE)
            container = ft.Container(
                content=stack,
                on_click=self.make_toggle_event(i),
                data=ModelImage(hash=img)
            )
            containers.append(ImageView(container, icon))

        return containers

    def make_toggle_event(self, i: int):
        async def tog():
            await self.toggle_delete(i)
        return tog

    async def toggle_delete(self, i: int):
        if self._selected_image != None:
            selected = self._views[self._selected_image]
            data = cast(ModelImage, selected.container.data)
            await self._observer.notify("selected_images", ("delete", data))
            selected.icon.visible = False

        self._selected_image = i
        selected = self._views[self._selected_image]
        data = cast(ModelImage, selected.container.data)
        await self._observer.notify("selected_images", ("add", data))
        selected.icon.visible = True

        self.update()

