
from datetime import datetime, timezone

from driftctl.core.diff import compare_snapshots
from driftctl.core.models import Observation, Snapshot


def make_snapshot(status_code: int):
    return Snapshot(
        target="127.0.0.1:8080",
        timestamp=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/api/users",
                metadata={
                    "status_code": status_code
                },
            )
        ],
    )


def test_changed_endpoint():
    previous = make_snapshot(401)
    current = make_snapshot(200)

    changes = compare_snapshots(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "CHANGED"
    assert changes[0].value == "/api/users"


def test_new_endpoint():
    previous = Snapshot(
        target="127.0.0.1:8080",
        timestamp=datetime.now(timezone.utc),
        observations=[],
    )

    current = Snapshot(
        target="127.0.0.1:8080",
        timestamp=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/admin",
                metadata={
                    "status_code": 200
                },
            )
        ],
    )

    changes = compare_snapshots(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "NEW"
    assert changes[0].value == "/admin"


def test_removed_endpoint():
    previous = Snapshot(
        target="127.0.0.1:8080",
        timestamp=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/admin",
                metadata={
                    "status_code": 200
                },
            )
        ],
    )

    current = Snapshot(
        target="127.0.0.1:8080",
        timestamp=datetime.now(timezone.utc),
        observations=[],
    )

    changes = compare_snapshots(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "REMOVED"
    assert changes[0].value == "/admin"

