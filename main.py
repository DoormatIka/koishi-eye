import multiprocessing
import flet as ft

from src.gui.gui import flet_main
from src.gui.config import config as flet_config

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    multiprocessing.freeze_support()

    _ = ft.run( # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        before_main=flet_config, 
        main=flet_main,
        assets_dir="img"
    ) 

