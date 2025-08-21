from fastapi import HTTPException


ERROR: dict[str, tuple[int, str]] = {
    "404": (
        404,
        "Not found"
    ),
    "500": (
        500,
        "internal server error"
    ),
}

def error(equipment_id: str) -> None:
    for i, (code, msg) in ERROR.items():
        if equipment_id.endswith(i):
            raise HTTPException(
                status_code=code,
                detail=msg,
            )