from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import datetime, timedelta


async def my_task():
    """
    Асинхронная задача, которую нужно запланировать.
    """
    print(f"Задача выполняется в {datetime.now()}")


async def main():
    """
    Создает и запускает асинхронный планировщик APScheduler.
    """
    scheduler = AsyncIOScheduler()

    # Планируем задачу my_task для выполнения через 10 секунд
    scheduler.add_job(my_task, "date", run_date=datetime.now() + timedelta(seconds=20))

    scheduler.start()

    print("Планировщик запущен, ждем выполнения задачи...")

    # Держим event loop активным, чтобы планировщик мог работать
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Останавливаем планировщик при завершении программы
        scheduler.shutdown()
        print("Планировщик остановлен")


if __name__ == "__main__":
    asyncio.run(main())
