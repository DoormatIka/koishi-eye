
import flet as ft

from gui.infra.router import Router
from gui.views.entry import entry_page

from gui.infra.app_bus import AppState, AppEventBus

async def flet_main(page: ft.Page):
    state = AppState()
    observer = AppEventBus(state)

    router = Router(page=page)
    await page.push_route("/")

    router.add_route(route="/main", container=entry_page(page, state, observer))

    await page.push_route("/main")

