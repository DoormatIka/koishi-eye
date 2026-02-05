
import flet as ft

from gui.router.router import Router
from gui.views.entry import entry_page


async def flet_main(page: ft.Page):
    router = Router(page=page)
    await page.push_route("/")

    router.add_route(route="/main", container=entry_page())

    await page.push_route("/main")

