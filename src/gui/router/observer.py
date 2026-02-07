
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import inspect
from typing import Literal

from gui.payload_types import SelectedImageResult

@dataclass
class AppState:
    directory: str | None = None
    selected_images: dict[str, SelectedImageResult] = field(default_factory=dict)

class Event:
    # base class for typed events. subclass with dataclasses for payloads.
    pass

StateKey = Literal[
    "directory", 
    "modify_selected_images",
    "MATCHES",
    "DELETE_SEL_IMG",
    "SEVERE_APP_ERROR",
]
ObserverFn = Callable[[AppState, object], None | Awaitable[None]]


class EventBus:
    state: AppState
    _fns: dict[StateKey, list[ObserverFn]]
    def __init__(self, state: AppState):
        self.state = state
        self._fns = {}
    def subscribe(self, key: StateKey, on_key: ObserverFn):
        if key not in self._fns:
            self._fns[key] = []
        self._fns[key].append(on_key)

    async def notify(self, key: StateKey, payload: object):
        if key not in self._fns:
            return

        for fn in self._fns[key]:
            try:
                if inspect.iscoroutinefunction(fn):
                    await fn(self.state, payload)
                else:
                    _ = fn(self.state, payload)
            except Exception as e:
                print(f"Subscriber failed for {key}: \n\t{e}")
                await self.notify("SEVERE_APP_ERROR", e)
