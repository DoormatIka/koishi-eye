
import flet as ft


def flet_main(page: ft.Page):
    page.title = "koishi's eye"
    page.window.resizable = True
    page.window.width = 700
    page.window.height = 400

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = None

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
        alignment=ft.Alignment.CENTER,
        content=row,
        expand=True,
    )

    page.add(c)


