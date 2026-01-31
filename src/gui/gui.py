
import flet as ft
import pprint

from hashers.types import CombinedImageHash


weight_clrs = {
    ft.Colors.AMBER_800: 5,
    ft.Colors.BLUE_800: 10,
}

def create_pair_image() -> ft.Container:
    im = ft.Container(
        content=ft.Image(
            src="/home/mualice/Downloads/2025-11-15_14.30.53.png",
            height=150,
            fit=ft.BoxFit.COVER,
            expand=1,
        ),
        on_click=lambda a: {}
    )
    img_row = ft.Row(
        controls=[im for _ in range(0, 5)],
        alignment=ft.MainAxisAlignment.START,
        scroll=ft.ScrollMode.ADAPTIVE,
        width=float("inf"),
    )

    c = ft.Column(
        controls=[img_row]
    )
    co = ft.Container(
        content=c,
        padding=10,
        border_radius=5,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREY_300),
    )

    return co
  
def counter():
    txt = ft.Text(value="0", text_align=ft.TextAlign.CENTER, width=100)

    def minus_click(_: ft.Event[ft.IconButton]):
        txt.value = str(int(txt.value) - 1)
    def plus_click(_: ft.Event[ft.IconButton]):
        txt.value = str(int(txt.value) + 1)

    row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
            txt,
            ft.IconButton(ft.Icons.ADD, on_click=plus_click)
        ],
    )

    c = ft.Container(
        content=row,
        bgcolor=ft.Colors.random(weights=weight_clrs),
        expand=True
    )

    return c

def flet_main(page: ft.Page):

    async def fp():
        q = await ft.FilePicker().get_directory_path(dialog_title="pick folder to scan")
        pprint.pprint(q)
        return q

    btn = ft.Button(
        content="Pick folder",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=fp,
        style=ft.ButtonStyle(
            padding=ft.Padding.only(left=20, right=20)
        )
    )

    c = ft.Container(
        content=btn,
        bgcolor=ft.Colors.random(weights=weight_clrs),
    )

    col = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            create_pair_image(),
            # counter(),
        ],
    )

    c = ft.Container(
        alignment=ft.Alignment.CENTER,
        content=col,
        expand=True,
    )

    page.add(c)


