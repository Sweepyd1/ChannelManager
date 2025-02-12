from apscheduler.schedulers.asyncio import AsyncIOScheduler

import asyncio
from datetime import datetime, timedelta

from typing import Callable, Any
import functools


class Schedule:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler_started = False

    async def start(self):
        self.scheduler.start()

    async def _new_task(self, task, *args, **kwargs):
        """Добавляет и запускает задачу в планировщик."""

        self.scheduler.add_job(
            task,
            "date",
            run_date=datetime.now() + timedelta(seconds=15),
            args=args,
            kwargs=kwargs,
        )

        if not self.scheduler_started:
            self.scheduler.start()
            self.scheduler_started = True
        print("Планировщик запущен, ждем выполнения задачи...")

    def new_scheduler(self):
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped(*args, **kwargs) -> Any:
                await self._new_task(func, *args, **kwargs)

            return wrapped

        return wrapper

    async def _stop_scheduler(self):
        """Останавливает планировщик."""
        if self.scheduler_started:
            self.scheduler.shutdown()
            print("Планировщик остановлен")
            self.scheduler_started = False
