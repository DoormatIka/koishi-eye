
import flet as ft

"""
BROKEN (assumptions as to why it isn't working):

# https://docs.flet.dev/controls/page/#flet.Page.push_route
- in user defined route_change(), the example directly appends to views.
- push_route() fires on_route_change.
"""
class Router:
    page: ft.Page
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: dict[str, ft.Container] = {}
        self.page.on_route_change = self.on_route_change

    def on_route_change(self, e: ft.RouteChangeEvent):
        self.page.views.clear()
        container = self.routes.get(e.route)
        if container == None:
            container = ft.Text("404 - Page Not Found.")

        view = ft.View(
            route=e.route,
            controls=[container]
        )

        self.page.views.append(view)


    def add_route(self, route: str, container: ft.Container):
        self.routes[route] = container

