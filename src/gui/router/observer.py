
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import inspect
from typing import Literal

from gui.models.image import ModelImage

@dataclass
class AppState:
    directory: str | None = None
    selected_images: set[ModelImage] = field(default_factory=set)

StateKey = Literal[
    "directory", 
    "selected_images"
]
# add AppState to Callable soon.
ObserverFn = Callable[[AppState, object], None | Awaitable[None]]


class Observer:
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
        if key in self._fns:
            for fn in self._fns[key]:
                if inspect.iscoroutinefunction(fn):
                    await fn(self.state, payload)
                else:
                    _ = fn(self.state, payload)
