from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Observation(BaseModel):
    type: str
    value: str
    metadata: dict = Field(default_factory=dict)


class Snapshot(BaseModel):
    target: str
    timestamp: datetime
    observations: list[Observation] = Field(default_factory=list)

    @classmethod
    def create(cls, target: str, observations: list[Observation]):
        return cls(
            target=target,
            timestamp=datetime.now(timezone.utc),
            observations=observations,
        )
