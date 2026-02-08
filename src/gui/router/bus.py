
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import inspect
from typing import Any, Generic, TypeVar, cast

from gui.payload_types import Event, SelectedPayload, SevereAppError

from finders import FinderInterface, ImagePair
from hashers import CombinedImageHash


@dataclass
class AppState:
    directory: str | None = None
    total_images: int = field(default_factory=int)
    selected_images: dict[str, SelectedPayload] = field(default_factory=dict)

    def __init__(self):
        pass


EventT = TypeVar("EventT", bound=Event)


Ctx = TypeVar("Ctx")
Observer = Callable[[Ctx, EventT], None | Awaitable[None]]
RuntimeObserver = Callable[[Any, Event], Any] # pyright: ignore[reportExplicitAny]
BusError = Callable[[Ctx, Event, Exception], Awaitable[None]]

class PureEventBus(Generic[Ctx]):
    _fns: dict[type[Event], list[RuntimeObserver]]
    on_error: BusError[Ctx]
    def __init__(self, on_error: BusError[Ctx]):
        self._fns = {}
        self.on_error = on_error
    def subscribe(self, event: type[EventT], handler: Observer[Ctx, EventT]) -> None:
        if event not in self._fns:
            self._fns[event] = []
        self._fns[event].append(cast(RuntimeObserver, handler))

    async def notify(self, ctx: Ctx, event: Event):
        handlers = list(self._fns.get(type(event), []))
        if not handlers:
            return

        for fn in handlers:
            try:
                if inspect.iscoroutinefunction(fn):
                    await fn(ctx, event)
                else:
                    _ = fn(ctx, event) # pyright: ignore[reportAny]
            except Exception as e:
                await self.on_error(ctx, event, e)


UIObserver = Callable[[AppState, EventT], None | Awaitable[None]]
class AppEventBus:
    bus: PureEventBus[AppState]
    state: AppState
    def __init__(self, state: AppState):
        self.state = state
        self.bus = PureEventBus(on_error=self.on_error)

    async def on_error(self, _: AppState, event: Event, e: Exception):
        if isinstance(event, SevereAppError):
            print(f"Recursed SEVERE_APP_ERROR handler exception: ", e)
        else:
            await self.notify(SevereAppError(e))

    def subscribe(self, event: type[EventT], handler: UIObserver[EventT]) -> None:
        self.bus.subscribe(event, handler)

    async def notify(self, event: Event):
        await self.bus.notify(self.state, event)
