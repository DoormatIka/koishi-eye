
import flet as ft

class Router:
    page: ft.Page
    routes: dict[str, ft.Container] = {}
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.on_route_change = self.on_route_change

    def on_route_change(self, e: ft.RouteChangeEvent):
        self.page.views.clear()
        container = self.routes.get(e.route)
        print(e)
        if container == None:
            return

        view = ft.View(
            route=e.route,
            controls=[container]
        )
        self.page.views.append(view)

        self.page.update()

    def pop(self, e: ft.RouteChangeEvent):
        pass

    def add_route(self, route: str, container: ft.Container):
        self.routes[route] = container

