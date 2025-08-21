import asyncio
from fastapi import (
    FastAPI,
)
from app.common.logging import config_log
from app.validators.validators import EquipmentId
from .models import (
    Equipment,
)
from .triggers import error


logger = config_log("service_a")

app = FastAPI(
    title="Service_a",
)

@app.post("/api/v1/equipment/cpe/{id}")
async def post_equipment(id: EquipmentId, body: Equipment):
    logger.info("request A: id=%s timeout=%s", id, body.timeoutInSeconds)
    error(id)
    await asyncio.sleep(60)
    logger.info("response A: id=%s code=200", id)
    return {
        "code": 200,
        "message": "success"
    }
        
@app.get("/health")
async def health_a():
    return {
        "ok": True
    }