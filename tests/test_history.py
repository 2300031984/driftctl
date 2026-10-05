from datetime import datetime, timezone
from pathlib import Path

from driftctl.core.history import build_history
from driftctl.core.models import Observation, Snapshot
from driftctl.storage.snapshots import save_snapshot


def create_test_snapshot(
    target: str,
    observations: list[Observation],
    timestamp: datetime,
):
    snapshot = Snapshot(
        target=target,
        timestamp=timestamp,
        observations=observations,
    )

    save_snapshot(snapshot)


def test_history_detects_new_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    target = "history-test"

    first_time = datetime(
        2026,
        10,
        5,
        20,
        0,
        tzinfo=timezone.utc,
    )

    second_time = datetime(
        2026,
        10,
        5,
        21,
        0,
        tzinfo=timezone.utc,
    )

    create_test_snapshot(
        target,
        [
            Observation(
                type="http_endpoint",
                value="/",
                metadata={
                    "status_code": 200,
                },
            )
        ],
        first_time,
    )

    create_test_snapshot(
        target,
        [
            Observation(
                type="http_endpoint",
                value="/",
                metadata={
                    "status_code": 200,
                },
            ),
            Observation(
                type="http_endpoint",
                value="/admin",
                metadata={
                    "status_code": 200,
                },
            ),
        ],
        second_time,
    )

    events = build_history(target)

    assert len(events) == 1
    assert events[0].change_type == "NEW"
    assert events[0].value == "/admin"


def test_history_detects_status_change(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    target = "history-test"

    first_time = datetime(
        2026,
        10,
        5,
        20,
        0,
        tzinfo=timezone.utc,
    )

    second_time = datetime(
        2026,
        10,
        5,
        21,
        0,
        tzinfo=timezone.utc,
    )

    create_test_snapshot(
        target,
        [
            Observation(
                type="http_endpoint",
                value="/api/users",
                metadata={
                    "status_code": 401,
                },
            )
        ],
        first_time,
    )

    create_test_snapshot(
        target,
        [
            Observation(
                type="http_endpoint",
                value="/api/users",
                metadata={
                    "status_code": 200,
                },
            )
        ],
        second_time,
    )

    events = build_history(target)

    assert len(events) == 1
    assert events[0].change_type == "CHANGED"
    assert events[0].value == "/api/users"
    assert events[0].previous["status_code"] == 401
    assert events[0].current["status_code"] == 200


def test_history_requires_two_snapshots(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    target = "history-test"

    timestamp = datetime(
        2026,
        10,
        5,
        20,
        0,
        tzinfo=timezone.utc,
    )

    create_test_snapshot(
        target,
        [
            Observation(
                type="http_endpoint",
                value="/",
                metadata={
                    "status_code": 200,
                },
            )
        ],
        timestamp,
    )

    events = build_history(target)

    assert events == []
