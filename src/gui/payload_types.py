
from dataclasses import dataclass
from typing import Literal
from gui.models.image import ModelImage

import flet as ft

class Event:
    # base class for typed events. subclass with dataclasses for payloads.
    pass

# payloads
@dataclass
class Directory(Event):
    directory: str | None

@dataclass
class SelectedPayload:
    id: str
    row: ft.Container
    model: ModelImage

@dataclass
class SelectedAction(Event):
    action: Literal["add", "delete"]
    payload: SelectedPayload | None

@dataclass
class ImageUpdate(Event):
    total: int

@dataclass
class DeleteAllSelected(Event):
    pass

@dataclass
class SevereAppError(Event):
    error: Exception

@dataclass
class ProgressUpdated(Event): # tie this to the cli logger.
    current: int
    total: int
    log: str
