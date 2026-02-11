
from src.gui.events import SelectedPayload

from collections.abc import Awaitable, Callable
from typing import TypeVar

from src.gui.events import UIEvent, SevereAppError
from src.gui.infra.bus import PureEventBus
from src.gui.infra.logger import Logger, QueueLogger

from src.finders import Buckets, FinderInterface, HammingClustererFinder, ImagePair
from src.hashers import ImageHasher


class AppState:
    directory: str | None
    total_images: int
    selected_images: dict[str, SelectedPayload]
    logger: Logger
    finder: FinderInterface[Buckets, set[ImagePair]]

    def __init__(self, queue_logger: QueueLogger, logger: Logger):
        self.total_images = 0
        self.selected_images = dict()
        self.logger = logger
        self.directory = None
        hasher = ImageHasher()
        self.finder = HammingClustererFinder(hasher=hasher, logger=queue_logger)

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
    def unsubscribe(self, event: type[UIEventT], handler: UIObserver[UIEventT]) -> None:
        self.bus.unsubscribe(event, handler)

    async def notify(self, event: UIEvent):
        await self.bus.notify(self.state, event)
