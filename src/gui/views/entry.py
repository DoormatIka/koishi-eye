
import pprint
import flet as ft


from src.gui.components.paginglist import PagingList
from src.gui.components.task_row import TaskRow
from src.gui.components.upper_row.upper_row import UpperBar
from src.gui.infra.app_bus import AppState, AppEventBus
from src.gui.events import Directory, ImageUpdate, SevereAppError
from src.gui.infra.logger import Logger, Progress

"""
Hello! This code uses an event bus to pass data around the UI.
"""


def entry_page(page: ft.Page, state: AppState, logger: Logger, bus: AppEventBus):
    manage_app_errors = make_manage_errors(page)

    bus.subscribe(Directory, manage_directory)
    bus.subscribe(ImageUpdate, image_update)
    bus.subscribe(SevereAppError, manage_app_errors)

    state.logger.subscribe(Progress, on_progress)


    col = ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            UpperBar(bus, logger),
            PagingList(bus, expand=True, page_size=20),
            TaskRow(bus),
        ],
    )

    return ft.Container(
        content=col,
        expand=True,
    )

def on_progress(_: None, payload: Progress):
    pprint.pprint(payload)

def make_manage_errors(page: ft.Page):
    snack_bar = ft.SnackBar(
        content=ft.Text("Error: "),
        action="Close",
        on_action=lambda _: page.pop_dialog(),
        bgcolor=ft.Colors.RED_100
    )

    def manage_app_errors(_: AppState, payload: SevereAppError):
        snack_bar.content = ft.Text(f"Error: {payload}")
        if not snack_bar.open:
            page.show_dialog(snack_bar)
        page.update() # pyright: ignore[reportUnknownMemberType]

    return manage_app_errors

def manage_directory(state: AppState, payload: Directory):
    state.total_images = 0
    state.directory = payload.directory

def image_update(state: AppState, payload: ImageUpdate):
    state.total_images = payload.total
