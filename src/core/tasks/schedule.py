from apscheduler.schedulers.asyncio import AsyncIOScheduler

import asyncio
from datetime import datetime, timedelta

from typing import Callable, Any
import functools


class Schedule:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler_started = False

    async def new_task(self, task, *args, **kwargs):
        """Добавляет и запускает задачу в планировщик."""
        self.scheduler.add_job(
            task,
            "date",
            run_date=datetime.now() + timedelta(seconds=10),
            args=args,
            kwargs=kwargs,
        )

        if not self.scheduler_started:
            self.scheduler.start()
            self.scheduler_started = True
            print("Планировщик запущен, ждем выполнения задачи...")

    def new_scheduler(self):
        """Декоратор для добавления функции в планировщик."""

        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped(*args, **kwargs) -> Any:
                await self.new_task(
                    func, *args, **kwargs
                )  # Передаем аргументы в new_task
                # return await func(*args, **kwargs)

            return wrapped

        return wrapper

    async def stop_scheduler(self):
        """Останавливает планировщик."""
        if self.scheduler_started:
            self.scheduler.shutdown()
            print("Планировщик остановлен")
            self.scheduler_started = False
