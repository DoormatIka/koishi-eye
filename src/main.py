import flet as ft

from gui import flet_config, flet_main

if __name__ == "__main__":
    _ = ft.run(before_main=flet_config, main=flet_main) # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

