
from collections.abc import Awaitable, Callable
import inspect
from typing import Any, Generic, TypeVar, cast

from src.gui.events import Event


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

    def unsubscribe(self, event: type[EventT], handler: Observer[Ctx, EventT]):
        if event in self._fns:
            self._fns[event].remove(handler)

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


