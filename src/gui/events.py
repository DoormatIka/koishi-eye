
from dataclasses import dataclass
from typing import Literal

from typing import TYPE_CHECKING


import flet as ft

if TYPE_CHECKING:
    from gui.models.image import ModelImage

class Event:
    # base class for typed events. subclass with dataclasses for payloads.
    pass

class UIEvent(Event):
    pass

# payloads
@dataclass
class Directory(UIEvent):
    directory: str | None

@dataclass
class SelectedPayload:
    id: str
    row: ft.Container
    model: "ModelImage"

@dataclass
class SelectedAction(UIEvent):
    action: Literal["add", "delete"]
    payload: SelectedPayload | None

@dataclass
class ImageUpdate(UIEvent):
    total: int

@dataclass
class DeleteAllSelected(UIEvent):
    pass

@dataclass
class SevereAppError(UIEvent):
    error: Exception

@dataclass
class ProgressUpdated(UIEvent): # tie this to the cli logger.
    current: int
    total: int
    log: str
