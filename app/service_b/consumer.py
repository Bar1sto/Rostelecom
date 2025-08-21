import json
from datetime import (
    datetime,
    timezone,
)
from fastapi import FastAPI
from .store import apply_res
from app.common.logging import config_log


logger = config_log("service_b.consumer")

async def consume_res(app: FastAPI):
    q = app.state.mq.result
    logger.info("result-consumer started")
    print(
        "[service_b] result-comsumer started"
    )
    async with q.iterator() as it:
        async for message in it:
            async with message.process():
                data = json.loads(message.body)
                if "finished_at" not in data or not data["finished_at"]:
                    data["finished_at"] = datetime.now(timezone.utc).isoformat()
                apply_res(data)
                
                print(
                    f"[service_b] updated task {data.get('task_id')}: {data.get('status')}"
                )