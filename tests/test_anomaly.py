from datetime import datetime, timezone

from driftctl.core.anomaly import detect_anomalies
from driftctl.core.baseline import Baseline
from driftctl.core.models import (
    Observation,
    Snapshot,
)


def test_detect_new_endpoint():

    baseline = Baseline(
        target="test",
        created_at=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/",
                metadata={
                    "status_code": 200,
                },
            )
        ],
    )

    snapshot = Snapshot(
        target="test",
        timestamp=datetime.now(timezone.utc),
        observations=[
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
    )

    anomalies = detect_anomalies(
        baseline,
        snapshot,
    )

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == "NEW"
    assert anomalies[0].value == "/admin"
    assert anomalies[0].risk == "MEDIUM"


def test_detect_authentication_change():

    baseline = Baseline(
        target="test",
        created_at=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/api/users",
                metadata={
                    "status_code": 401,
                },
            )
        ],
    )

    snapshot = Snapshot(
        target="test",
        timestamp=datetime.now(timezone.utc),
        observations=[
            Observation(
                type="http_endpoint",
                value="/api/users",
                metadata={
                    "status_code": 200,
                },
            )
        ],
    )

    anomalies = detect_anomalies(
        baseline,
        snapshot,
    )

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == "CHANGED"
    assert anomalies[0].risk == "HIGH"
    assert anomalies[0].baseline["status_code"] == 401
    assert anomalies[0].current["status_code"] == 200


def test_no_anomaly_when_snapshot_matches_baseline():

    observations = [
        Observation(
            type="http_endpoint",
            value="/",
            metadata={
                "status_code": 200,
            },
        )
    ]

    baseline = Baseline(
        target="test",
        created_at=datetime.now(timezone.utc),
        observations=observations,
    )

    snapshot = Snapshot(
        target="test",
        timestamp=datetime.now(timezone.utc),
        observations=observations,
    )

    anomalies = detect_anomalies(
        baseline,
        snapshot,
    )

    assert anomalies == []
