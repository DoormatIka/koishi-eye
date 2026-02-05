
import flet as ft

from gui.components.file_picker import FilePicker
from gui.components.card_images import ImageCardRow


weight_clrs = {
    ft.Colors.AMBER_800: 5,
    ft.Colors.BLUE_800: 10,
}


def entry_page():

    col = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ImageCardRow(matched_images=[]),
            FilePicker(),
        ],
    )

    return ft.Container(
        alignment=ft.Alignment.CENTER,
        content=col,
        expand=True,
    )



