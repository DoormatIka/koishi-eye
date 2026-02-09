
from gui.events import SelectedPayload

from collections.abc import Awaitable, Callable
from typing import TypeVar

from gui.events import UIEvent, SevereAppError
from gui.infra.bus import PureEventBus
from gui.infra.logger import Logger

from finders import Buckets, FinderInterface, HammingClustererFinder, ImagePair
from hashers import ImageHasher


class AppState:
    directory: str | None
    total_images: int
    selected_images: dict[str, SelectedPayload]
    logger: Logger
    finder: FinderInterface[Buckets, set[ImagePair]]

    def __init__(self):
        self.total_images = 0
        self.selected_images = dict()
        self.logger = Logger()
        self.directory = None

        hasher = ImageHasher(log=self.logger)
        self.finder = HammingClustererFinder(hasher=hasher)

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
