
from dataclasses import dataclass


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
