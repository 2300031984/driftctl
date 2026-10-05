from pathlib import Path

from driftctl.core.diff import compare_snapshots
from driftctl.core.findings import Finding
from driftctl.storage.snapshots import (
    list_snapshots,
    load_snapshot,
)


def build_evidence(
    finding: Finding,
) -> dict | None:

    snapshots = list_snapshots(
        finding.target
    )

    if len(snapshots) < 2:
        return None

    for index in range(1, len(snapshots)):

        previous_path = snapshots[index - 1]
        current_path = snapshots[index]

        previous = load_snapshot(
            previous_path
        )

        current = load_snapshot(
            current_path
        )

        changes = compare_snapshots(
            previous,
            current,
        )

        for change in changes:

            if change.value != finding.value:
                continue

            if change.change_type != finding.change_type:
                continue

            return {
                "finding_id": finding.id,
                "target": finding.target,
                "previous_snapshot": str(
                    previous_path
                ),
                "current_snapshot": str(
                    current_path
                ),
                "change_type": change.change_type,
                "observation_type": change.observation_type,
                "value": change.value,
                "previous": change.previous,
                "current": change.current,
                "risk": finding.risk,
                "reason": finding.reason,
                "fingerprint": finding.fingerprint,
            }

    return None
