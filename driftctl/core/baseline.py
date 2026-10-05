import json
from datetime import datetime, timezone
from pathlib import Path

from driftctl.core.models import Observation, Snapshot


BASELINE_DIR = Path("data/baselines")


class Baseline:
    def __init__(
        self,
        target: str,
        created_at: datetime,
        observations: list[Observation],
    ):
        self.target = target
        self.created_at = created_at
        self.observations = observations

    def model_dump(self) -> dict:
        return {
            "target": self.target,
            "created_at": self.created_at.isoformat(),
            "observations": [
                observation.model_dump()
                for observation in self.observations
            ],
        }


def create_baseline(
    snapshot: Snapshot,
) -> Baseline:

    return Baseline(
        target=snapshot.target,
        created_at=datetime.now(timezone.utc),
        observations=snapshot.observations,
    )


def save_baseline(
    baseline: Baseline,
) -> Path:

    BASELINE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_target = baseline.target.replace(
        ":",
        "_",
    )

    path = BASELINE_DIR / (
        f"{safe_target}.json"
    )

    path.write_text(
        json.dumps(
            baseline.model_dump(),
            indent=2,
        )
    )

    return path


def load_baseline(
    target: str,
) -> Baseline:

    safe_target = target.replace(
        ":",
        "_",
    )

    path = BASELINE_DIR / (
        f"{safe_target}.json"
    )

    data = json.loads(
        path.read_text()
    )

    observations = [
        Observation.model_validate(
            observation
        )
        for observation in data[
            "observations"
        ]
    ]

    return Baseline(
        target=data["target"],
        created_at=datetime.fromisoformat(
            data["created_at"]
        ),
        observations=observations,
    )
