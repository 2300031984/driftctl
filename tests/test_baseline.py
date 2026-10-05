from datetime import datetime, timezone

from driftctl.core.baseline import (
    create_baseline,
    load_baseline,
    save_baseline,
)
from driftctl.core.models import (
    Observation,
    Snapshot,
)


def test_create_baseline():

    snapshot = Snapshot(
        target="baseline-test",
        timestamp=datetime(
            2026,
            10,
            5,
            tzinfo=timezone.utc,
        ),
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
                value="/login",
                metadata={
                    "status_code": 200,
                },
            ),
        ],
    )

    baseline = create_baseline(
        snapshot
    )

    assert baseline.target == "baseline-test"
    assert len(
        baseline.observations
    ) == 2


def test_save_and_load_baseline(
    tmp_path,
    monkeypatch,
):

    monkeypatch.chdir(tmp_path)

    snapshot = Snapshot(
        target="baseline-test",
        timestamp=datetime(
            2026,
            10,
            5,
            tzinfo=timezone.utc,
        ),
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

    baseline = create_baseline(
        snapshot
    )

    path = save_baseline(
        baseline
    )

    assert path.exists()

    loaded = load_baseline(
        "baseline-test"
    )

    assert loaded.target == (
        "baseline-test"
    )

    assert len(
        loaded.observations
    ) == 1

    assert (
        loaded.observations[0].value
        == "/api/users"
    )

    assert (
        loaded.observations[0]
        .metadata["status_code"]
        == 401
    )
