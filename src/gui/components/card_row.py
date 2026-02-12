
from collections.abc import Collection
from dataclasses import dataclass
from typing import Any, Callable, Literal, cast
import uuid
import flet as ft

from src.finders import ImagePair
from src.hashers.types import CombinedImageHash
from src.gui.models.image import ModelImage

@dataclass
class ImageView:
    container: ft.Container
    icon: ft.Icon

class ImageCardRow(ft.Container):
    id: str
    content: ft.Control | None
    padding: ft.PaddingValue | None
    border_radius: ft.BorderRadiusValue | None
    bgcolor: ft.ColorValue | None
    width: float | None

    _on_select: Callable[[ImagePair, bool], None]
    _pair: ImagePair
    _views: list[ImageView]
    _selected_image: int | None
    def __init__(
        self, 
        pair: ImagePair,
        on_select: Callable[[ImagePair, bool], None],
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
        self.id = str(uuid.uuid4())
        self._on_select = on_select
        self._pair = pair
        views = self.create_model_images(pair)

        img_row = ft.Row(
            controls=[view.container for view in views],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE,
            height=180
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
                height=200,
                width=150,
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
            self.toggle_delete(i)
        return tog

    def _deselect_current(self):
        """Handles the UI and Bus notification for removing a selection."""
        if self._selected_image is None:
            return

        view = self._views[self._selected_image]
        view.icon.visible = False
        view.icon.update()
        
        self._on_select(self._pair, False)

    def _select_new(self, i: int):
        """Handles the UI and Bus notification for adding a selection."""
        self._selected_image = i
        view = self._views[i]
        view.icon.visible = True
        view.icon.update()
        
        self._on_select(self._pair, True)


    def toggle_delete(self, i: int):
        """Entry point for the click event."""
        if self._selected_image == i:
            self._deselect_current()
            self._selected_image = None
        else:
            if self._selected_image is not None:
                self._deselect_current()
            
            self._select_new(i)

