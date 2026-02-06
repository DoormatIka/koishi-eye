
from dataclasses import dataclass
from typing import Literal
from gui.models.image import ModelImage

import flet as ft

SelectedImageActions = Literal["add", "delete"]
@dataclass
class SelectedImageResult:
    id: str
    row: ft.Container
    model: ModelImage
SelectedImageAction = tuple[SelectedImageActions, SelectedImageResult]

DirectoryResult = str

