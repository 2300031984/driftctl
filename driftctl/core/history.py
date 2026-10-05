from dataclasses import dataclass
from pathlib import Path

from driftctl.core.diff import Change, compare_snapshots
from driftctl.core.risk import classify_change
from driftctl.storage.findings import find_by_fingerprint
from driftctl.storage.snapshots import (
    list_snapshots,
    load_snapshot,
)


@dataclass
class HistoryEvent:
    previous_snapshot: Path
    current_snapshot: Path
    change_type: str
    observation_type: str
    value: str
    previous: dict | None
    current: dict | None
    risk: str
    reason: str
    finding_id: str | None = None


def build_history(target: str) -> list[HistoryEvent]:
    snapshots = list_snapshots(target)

    if len(snapshots) < 2:
        return []

    events = []

    for index in range(1, len(snapshots)):

        previous_path = snapshots[index - 1]
        current_path = snapshots[index]

        previous = load_snapshot(previous_path)
        current = load_snapshot(current_path)

        changes = compare_snapshots(
            previous,
            current,
        )

        for change in changes:

            risk, reason = classify_change(
                change
            )

            finding = find_by_fingerprint(
                _create_fingerprint_change(
                    change,
                    target,
                )
            )

            finding_id = (
                finding.id
                if finding
                else None
            )

            events.append(
                HistoryEvent(
                    previous_snapshot=previous_path,
                    current_snapshot=current_path,
                    change_type=change.change_type,
                    observation_type=change.observation_type,
                    value=change.value,
                    previous=change.previous,
                    current=change.current,
                    risk=risk,
                    reason=reason,
                    finding_id=finding_id,
                )
            )

    return events


def _create_fingerprint_change(
    change: Change,
    target: str,
):
    from driftctl.core.findings import create_fingerprint

    return create_fingerprint(
        change,
        target,
    )
