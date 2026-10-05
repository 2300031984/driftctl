from dataclasses import dataclass

from driftctl.core.models import Observation, Snapshot


@dataclass
class Change:
    change_type: str
    observation_type: str
    value: str
    previous: dict | None
    current: dict | None


def observation_key(observation: Observation) -> tuple:
    return (
        observation.type,
        observation.value,
    )


def build_index(
    snapshot: Snapshot,
) -> dict[tuple, Observation]:

    return {
        observation_key(observation): observation
        for observation in snapshot.observations
    }


def compare_snapshots(
    previous: Snapshot,
    current: Snapshot,
) -> list[Change]:

    previous_index = build_index(previous)
    current_index = build_index(current)

    changes = []

    # New observations
    for key, observation in current_index.items():

        if key not in previous_index:

            changes.append(
                Change(
                    change_type="NEW",
                    observation_type=observation.type,
                    value=observation.value,
                    previous=None,
                    current=observation.metadata,
                )
            )

    # Removed observations
    for key, observation in previous_index.items():

        if key not in current_index:

            changes.append(
                Change(
                    change_type="REMOVED",
                    observation_type=observation.type,
                    value=observation.value,
                    previous=observation.metadata,
                    current=None,
                )
            )

    # Changed observations
    for key in previous_index.keys() & current_index.keys():

        old = previous_index[key]
        new = current_index[key]

        if old.metadata != new.metadata:

            changes.append(
                Change(
                    change_type="CHANGED",
                    observation_type=new.type,
                    value=new.value,
                    previous=old.metadata,
                    current=new.metadata,
                )
            )

    return changes
