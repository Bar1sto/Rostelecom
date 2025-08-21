from datetime import (
    datetime,
    timezone,
)


TASKS: dict[str, dict] = {}

def create_task_hand(task_id: str, equipment_id: str) -> None:
    TASKS[task_id] = {
        "status": "PENDING",
        "equipment_id": equipment_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
def get_task(task_id: str) -> dict | None:
    return TASKS.get(task_id)

def apply_res(res: dict) -> None:
    task_id = res.get("task_id")
    if not task_id:
        return
    rec = TASKS.get(task_id)
    if rec is None:
        TASKS[task_id] = rec = {}
    rec.update(
        {
            "status": res.get("status"),
            "code": res.get("code"),
            "message": res.get("message"),
            "finished_at": res.get("finished_at")
        }
    )