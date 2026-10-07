import json
from pathlib import Path

from driftctl.core.models import Snapshot


SNAPSHOT_DIR = Path("data/snapshots")


def save_snapshot(snapshot: Snapshot) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = snapshot.timestamp.strftime("%Y%m%dT%H%M%SZ")

    safe_target = (
        snapshot.target
        .replace("://", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    filename = f"{safe_target}_{timestamp}.json"

    path = SNAPSHOT_DIR / filename

    path.write_text(
        json.dumps(
            snapshot.model_dump(mode="json"),
            indent=2,
        )
    )

    return path

def load_snapshot(path: Path) -> Snapshot:
    data = json.loads(
        path.read_text()
    )

    return Snapshot.model_validate(data)


def list_snapshots(target: str) -> list[Path]:
    SNAPSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_target = (
        target
        .replace("://", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    pattern = f"{safe_target}_*.json"

    return sorted(
        SNAPSHOT_DIR.glob(pattern)
    )
