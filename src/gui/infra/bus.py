
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import inspect
from typing import Any, Generic, TypeVar, cast

from gui.events import Event, UIEvent, SelectedPayload, SevereAppError

@dataclass
class AppState:
    directory: str | None = None
    total_images: int = field(default_factory=int)
    selected_images: dict[str, SelectedPayload] = field(default_factory=dict)



EventT = TypeVar("EventT", bound=Event)

Ctx = TypeVar("Ctx")
Observer = Callable[[Ctx, EventT], None | Awaitable[None]]
RuntimeObserver = Callable[[Ctx, Any], Any] # pyright: ignore[reportExplicitAny]
BusError = Callable[[Ctx, Any, Exception], Awaitable[None]] # pyright: ignore[reportExplicitAny]

class PureEventBus(Generic[Ctx]):
    _fns: dict[type[Any], list[RuntimeObserver[Ctx]]] # pyright: ignore[reportExplicitAny]
    on_error: BusError[Ctx]

    def __init__(self, on_error: BusError[Ctx]):
        self._fns = {}
        self.on_error = on_error

    def subscribe(self, event: type[EventT], handler: Observer[Ctx, EventT]) -> None:
        if event not in self._fns:
            self._fns[event] = []
        self._fns[event].append(cast(RuntimeObserver[Ctx], handler))

    async def notify(self, ctx: Ctx, event: Any): # pyright: ignore[reportAny, reportExplicitAny]
        handlers = list(self._fns.get(type(event), [])) # pyright: ignore[reportAny, reportUnknownArgumentType]
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

# ALL THIS EFFORT TO MAKE CODE THAT'S CLEAN FUCK

UIEventT = TypeVar("UIEventT", bound=UIEvent)
UIObserver = Callable[[AppState, UIEventT], None | Awaitable[None]]
class AppEventBus:
    bus: PureEventBus[AppState]
    state: AppState
    def __init__(self, state: AppState):
        self.state = state
        self.bus = PureEventBus(on_error=self.on_error)

    async def on_error(self, _: AppState, event: UIEvent, e: Exception):
        if isinstance(event, SevereAppError):
            print(f"Recursed SEVERE_APP_ERROR handler exception: ", e)
        else:
            await self.notify(SevereAppError(e))

    def subscribe(self, event: type[UIEventT], handler: UIObserver[UIEventT]) -> None:
        self.bus.subscribe(event, handler)

    async def notify(self, event: UIEvent):
        await self.bus.notify(self.state, event)

