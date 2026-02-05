
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import inspect
from typing import Any, Literal, TypeGuard

@dataclass
class AppState:
    directory: str | None = None

StateKey = Literal["directory"]
ObserverFn = Callable[[object], None]

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

    def notify(self, key: StateKey, payload: object):
        # Update the actual state first
        setattr(self.state, key, payload)
        
        # Tell everyone about it
        if key in self._fns:
            for fn in self._fns[key]:
                fn(payload)
