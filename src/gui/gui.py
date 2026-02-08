
import flet as ft

from gui.router.router import Router
from gui.views.entry import entry_page

from gui.router.bus import AppState, AppEventBus

async def flet_main(page: ft.Page):
    observer = AppEventBus(AppState())

    router = Router(page=page)
    await page.push_route("/")

    router.add_route(route="/main", container=entry_page(page, observer))

    await page.push_route("/main")

