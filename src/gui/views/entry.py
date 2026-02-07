
from typing import cast
import flet as ft

from gui.components.card_list import FileCardList

from gui.components.task_row import TaskRow
from gui.components.upper_row.upper_row import UpperBar
from gui.router.observer import AppState, EventBus
from gui.payload_types import DirectoryResult, SelectedImageAction

"""
Hello! This code uses an event bus to pass data around the UI.
"""

def entry_page(page: ft.Page, bus: EventBus):
    manage_app_errors = make_manage_errors(page)

    bus.subscribe("directory", manage_directory)
    bus.subscribe("modify_selected_images", manage_selected_images)
    bus.subscribe("DELETE_SEL_IMG", delete_selected_images)
    bus.subscribe("SEVERE_APP_ERROR", manage_app_errors)


    col = ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            UpperBar(bus=bus),
            FileCardList(
                bus=bus,
                expand=True,
            ),
            TaskRow(bus=bus),
        ],
    )

    return ft.Container(
        content=col,
        expand=True,
    )

def make_manage_errors(page: ft.Page):
    snack_bar = ft.SnackBar(
        content=ft.Text("Error: "),
        action="Close",
        on_action=lambda _: page.pop_dialog(),
        bgcolor=ft.Colors.RED_100
    )

    def manage_app_errors(_: AppState, payload: object):
        snack_bar.content = ft.Text(f"Error: {payload}")
        if not snack_bar.open:
            page.show_dialog(snack_bar)
        page.update() # pyright: ignore[reportUnknownMemberType]

    return manage_app_errors

def manage_directory(state: AppState, payload: object):
    if isinstance(payload, DirectoryResult):
        state.directory = payload

def manage_selected_images(state: AppState, payload: object):
    action, res = cast(SelectedImageAction, payload)

    if action == "add":
        state.selected_images[res.id] = res

    if action == "delete":
        _ = state.selected_images.pop(res.id)

def delete_selected_images(state: AppState, _: object):
    for row_id, result in list(state.selected_images.items()):
        parent = result.row.parent
        if isinstance(parent, (ft.Column, ft.Row, ft.ListView)):
            try:
                parent.controls.remove(result.row)
                print(f"Row: {result.id}, {result.model.path} is deleted.")
                parent.update()
            except (ValueError, Exception) as e:
                print(f"Error on manage_selected_images: {e}")
    
    state.selected_images.clear()

