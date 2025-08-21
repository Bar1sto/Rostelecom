import asyncio
import json
import httpx
from datetime import (
    datetime,
    timezone,
)
from app.common import settings
from app.common.mq import pub_json
from app.common.logging import config_log


logger = config_log("worker.processor")

async def one_process(message, exch, sem):
    async with sem:
        async with message.process():
            data = json.loads(message.body)
            task_id = data["task_id"]
            equipment_id = data['equipment_id']
            payload = data["payload"]
            url = f"{settings.SERVICE_A_URL}/api/v1/equipment/cpe/{equipment_id}"
            timeout = payload["timeoutInSeconds"] + settings.REQUEST_TIMEOUT_BUFFER
           
            logger.info("call A url=%s timeout=%ss task=%s", url, timeout, task_id)
            
            status_code = 500
            for attempt in range(1, settings.MAX_RETRIES + 1):
                try:
                    async with httpx.AsyncClient(
                        verify=settings.A_VERIFY_TLS 
                    ) as client:
                        res = await client.post(
                                url,
                                json=payload,
                                timeout=timeout
                            )
                        status_code = res.status_code
                    if status_code in (200, 404):
                        break
                    if attempt < settings.MAX_RETRIES:
                        await asyncio.sleep(settings.BACKOFF_BASE * (2 ** (attempt -1)))
                        continue
                    break
                except (
                    httpx.TimeoutException,
                    httpx.RequestError
                ):
                    if attempt < settings.MAX_RETRIES:
                        await asyncio.sleep(settings.BACKOFF_BASE * (2 ** (attempt - 1)))
                        continue
                    status_code = 500
                    break

            if status_code == 200:
                outcome = {
                    "status": "COMPLETED",
                    "code": 200,
                    "message": "success"
                }
            elif status_code == 404:
                outcome = {
                    "status": "NOT_FOUND",
                    "code": 404,
                    "message": "Equipment not found"
                }
            else:
                outcome = {
                    "status": "FAILED",
                    "code": 500,
                    "message": f"A responded {status_code}"
                }
            result_msg = {
                "task_id": task_id,
                **outcome,
                "finished_at": datetime.now(timezone.utc).isoformat(),
            }
            await pub_json(
                    exch,
                    "task.result",
                    result_msg
                )
            
            logger.info("published result task=%s status=%s", task_id, outcome["status"])
            
            print(
            f"[worker] publisher result for task {task_id}: {outcome['status']}"
            )
            