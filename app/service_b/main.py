import asyncio
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from uuid import uuid4
from app.validators.validators import EquipmentId
from fastapi import (
    FastAPI,
)
from app.common.mq import(
    mq_lifespan,
    pub_json,
)
from app.service_a.models import Equipment
from .store import (
    TASKS,
    create_task_hand,
    get_task,
)
from .consumer import (
    consume_res,
)
from app.common.logging import config_log


logger = config_log("service_b")

def response_json(code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message
        }
    )
    
@asynccontextmanager
async def service_lifespan(app: FastAPI):
    async with mq_lifespan(app):
        task = asyncio.create_task(
            consume_res(app)
        )
        app.state.result_consumer_task = task
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(
                task,
                return_exceptions=True
            )
            
app = FastAPI(
    title="Service B",
    lifespan=service_lifespan,
)

@app.post("/api/v1/equipment/cpe/{id}")
async def create_task_handler(id: EquipmentId, body: Equipment):
    task_id = str(uuid4())
    logger.info("create_task id=%s task_id=%s", id, task_id)
    create_task_hand(task_id, id)
    msg = {
        "task_id": task_id,
        "equipment_id": id,
        "payload": body.model_dump(),
        "created_at": TASKS[task_id]["created_at"],
    }
    await pub_json(
        app.state.mq.exch,
        "task.create",
        msg,
    )
    logger.info("published task.create task_id=%s", task_id)
    return {
        "code": 200,
        "taskId": task_id
    }
    
    
@app.get("/api/v1/equipment/cpe/{id}/task/{task_id}")
async def task_status(id: EquipmentId, task_id: str):
    data = get_task(task_id)
    if not data:
        return response_json(
            404,
            "The requested task is not found"
        )
    if data["equipment_id"] != id:
        return response_json(
            404,
            "The requested equipment is not found"
        )
    
    status = data["status"]
    if status in ("PENDING", "RUNNING"):
        return response_json(
            204,
            "Task is still running"
        )
    if status == "COMPLETED":
        return response_json(
            200,
            "Completed"
        )
    if status == "FAILED":
        return response_json(
            500,
            "Internal provisioning exception"
        )
    if status == "NOT_FOUND":
        return response_json(
            404,
            "The requested equipment is not found"
        )
        

@app.get("/health")
async def health_b():
    has_mq = hasattr(app.state, "mq")
    has_consumer = hasattr(app.state, "result_consumer_task") and not app.state.result_consumer_task.done()
    return {
        "ok": True,
        "mq": bool(has_mq),
        "result_consumer": bool(has_consumer)
    }