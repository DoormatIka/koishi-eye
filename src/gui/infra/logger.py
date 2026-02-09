
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar
from typing import Protocol
import queue
import asyncio
from multiprocessing.queues import Queue

from src.gui.events import Event
from src.gui.infra.bus import PureEventBus


class LoggerEvent(Event):
    pass

@dataclass
class Info(LoggerEvent):
    msg: str

@dataclass
class Warn(LoggerEvent):
    msg: str

@dataclass
class Error(LoggerEvent):
    ex: str

@dataclass
class Progress(LoggerEvent): # we do not know the total number of files being scanned.
    path: Path
    is_complete: bool
    current: int


LoggerEventT = TypeVar("LoggerEventT", bound=LoggerEvent)
LoggerObserver = Callable[[None, LoggerEventT], None | Awaitable[None]]
class Logger:
    bus: PureEventBus[None]
    def __init__(self):
        self.bus = PureEventBus(on_error=self.on_error)

    async def on_error(self, _: None, event: LoggerEvent, e: Exception):
        if isinstance(event, Error):
            print(f"Recursed SEVERE_APP_ERROR handler exception: ", e)
        else:
            await self.notify(Error(str(e)))

    def subscribe(self, event: type[LoggerEventT], handler: LoggerObserver[LoggerEventT]) -> None:
        self.bus.subscribe(event, handler)

    async def notify(self, event: LoggerEvent):
        await self.bus.notify(None, event)


class HasherLogger(Protocol):
    """
    An multi-threaded adapter for the PureEventBus logger.
    """
    async def notify(self, event: LoggerEvent) -> None: ...

class QueueLogger:
    _queue: Queue[LoggerEvent]
    def __init__(self, queue: Queue[LoggerEvent]):
        self._queue = queue

    async def notify(self, event: LoggerEvent) -> None:
        # IMPORTANT: event must be picklable
        self._queue.put(event)

async def drain_log_queue(
    log_queue: Queue[LoggerEvent],
    logger: Logger,
):
    """
    The bridge of the multi-threaded adapter to the single-threaded event bus.
    """
    while True:
        try:
            event = log_queue.get(block=False)
        except queue.Empty:
            await asyncio.sleep(0.05)
            continue

        await logger.notify(event)

"""
class StyledCLILogger: # color code per log level: info, warn, match
    SAVE: str = "\033[s"
    RESTORE: str = "\033[u"
    CLEAR_DOWN: str = "\033[J"
    def __init__(self):
        _ = sys.stdout.write(self.SAVE)
        _ = sys.stdout.flush()

    def _draw(self, tag: str, s: str):
        _ = sys.stdout.write(self.RESTORE)
        _ = sys.stdout.write(self.CLEAR_DOWN)
        _ = sys.stdout.write(f"[{tag}] - {s}")
        _ = sys.stdout.flush()

    def next_line(self):
        _ = sys.stdout.write("\n")
        _ = sys.stdout.write(self.SAVE)
        _ = sys.stdout.flush()
    def info(self, s: str) -> None:
        self._draw("INFO", s)
    def warn(self, s: str) -> None:
        self._draw("WARN", s)
    def match(self, s: str) -> None:
        self.next_line()
        self._draw("MATCH", s)

    def progress(self) -> None:
        return
"""
