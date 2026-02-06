
import flet as ft

from gui.router.router import Router
from gui.views.entry import entry_page

from gui.router.observer import AppState, EventBus

async def flet_main(page: ft.Page):
    observer = EventBus(AppState())

    router = Router(page=page)
    await page.push_route("/")

    router.add_route(route="/main", container=entry_page(observer))

    await page.push_route("/main")

