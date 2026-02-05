
import flet as ft

from gui.components.card_list import FileCardList
from gui.components.file_picker import FilePicker
# from gui.components.card_images import ImageCardRow

from gui.router.observer import Observer

weight_clrs = {
    ft.Colors.AMBER_800: 5,
    ft.Colors.BLUE_800: 10,
}

def entry_page(observer: Observer):
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



