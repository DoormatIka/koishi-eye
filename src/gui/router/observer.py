
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

@dataclass
class AppState:
    directory: str | None = None

StateKey = Literal["directory"]
ObserverFn = Callable[[object], None]

class Observer:
    state: AppState
    _fns: dict[StateKey, ObserverFn]
    def __init__(self, state: AppState):
        self.state = state
        self._fns = {}
    def subscribe(self, key: StateKey, on_key: ObserverFn):
        self._fns[key] = on_key
    def notify(self, key: StateKey, payload: object):
        observer = self._fns.get(key)
        if observer == None:
            return
        observer(payload)
