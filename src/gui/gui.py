
import asyncio
import multiprocessing
from multiprocessing.queues import Queue as QueueType
import flet as ft

from src.gui.infra.logger import Logger, LoggerEvent, QueueLogger, drain_log_queue
from src.gui.infra.router import Router
from src.gui.views.entry import entry_page

from src.gui.infra.app_bus import AppState, AppEventBus

async def flet_main(page: ft.Page):
    logger = Logger()
    internal_queue: QueueType[LoggerEvent] = multiprocessing.Queue()
    queue_logger = QueueLogger(internal_queue)
    state = AppState(queue_logger=queue_logger, logger=logger)
    observer = AppEventBus(state)

    drain_task = asyncio.create_task(
        drain_log_queue(internal_queue, logger)
    )

    def on_disconnect(_):
        _ = drain_task.cancel()
        internal_queue.close()
    page.on_disconnect = on_disconnect


    router = Router(page=page)
    await page.push_route("/")

    router.add_route(route="/main", container=entry_page(page, state, logger, observer))

    await page.push_route("/main")

