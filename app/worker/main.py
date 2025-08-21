import asyncio
from app.common import settings
from app.common.mq import (
    open_mq,
    declare_topology,
)
from .processor import one_process
from app.common.logging import config_log


logger = config_log("worker")

async def run():
    conn, ch = await open_mq()
    try:
        exch, create, result = await declare_topology(ch)
        sem = asyncio.Semaphore(settings.WORKER_CONCURRENCY)
        logger.info("connected. waiting for messages")
        print(
            "[worker] подключен, ожидаю сообщения"
        )
        async with create.iterator() as it:
            async for message in it:
                asyncio.create_task(
                    one_process(
                        message,
                        exch,
                        sem,
                    )
                )
    finally:
        await ch.close()
        await conn.close()
        
        

if __name__ == "__main__":
    asyncio.run(run())
    