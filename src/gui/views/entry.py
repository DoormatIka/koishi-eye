
from typing import cast
import flet as ft

from gui.components.card_list import FileCardList
from gui.components.file_picker import FilePicker

from gui.router.observer import AppState, Observer
from gui.payload_types import DirectoryResult, SelectedImageResult

def entry_page(observer: Observer):
    observer.subscribe("directory", manage_directory)
    observer.subscribe("selected_images", manage_selected_images)

    col = ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            FileCardList(
                expand=True,
                observer=observer
            ),
            FilePicker(observer=observer),
        ],
    )

    return ft.Container(
        # alignment=ft.Alignment.CENTER,
        content=col,
        expand=True,
    )

def manage_directory(state: AppState, payload: object):
    if isinstance(payload, DirectoryResult):
        state.directory = payload

def manage_selected_images(state: AppState, payload: object):
    cmd, model_image = cast(SelectedImageResult, payload)
    if cmd == "add":
        state.selected_images.add(model_image)
    if cmd == "delete":
        state.selected_images.discard(model_image)


