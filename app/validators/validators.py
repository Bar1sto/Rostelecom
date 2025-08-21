from typing import Annotated, TypeAlias
from fastapi import Path


EquipmentId: TypeAlias = Annotated[
    str,
    Path(pattern=r"^[A-Za-z0-9]{6,}$"),
]
