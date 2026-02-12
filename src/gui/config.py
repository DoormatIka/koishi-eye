
import flet as ft

def config(page: ft.Page):
    page.title = "koisee"
    page.window.resizable = True
    page.window.width = 700
    page.window.height = 800
    page.window.min_width = 700
    page.window.min_height = 600

    def on_keyboard(e: ft.KeyboardEvent):
        if e.ctrl and e.key == "S":
            page.show_semantics_debugger = not page.show_semantics_debugger
            page.update() # pyright: ignore[reportUnknownMemberType]

    page.on_keyboard_event = on_keyboard

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = None
