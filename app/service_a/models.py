from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)
from typing import (
    List,
    Optional,
)


class Parameters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    password: str
    vlan: Optional[int] = Field(default=None, ge=1, le=4094)
    interfaces: List[int] = Field(min_length=1)
    
    @field_validator("interfaces")
    @staticmethod
    def interfasec_positive(cls, vlan: List[int]):
        if not all(i > 0 for i in vlan):
            raise ValueError(
                "interfasec must contain only positive integers"
            )
        return vlan

class Equipment(BaseModel):
    timeoutInSeconds: int = Field(
        ...,
        ge=1,
    )
    parameters: Parameters