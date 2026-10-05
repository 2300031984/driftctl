from dataclasses import dataclass

from driftctl.core.baseline import Baseline
from driftctl.core.diff import Change, observation_key
from driftctl.core.models import Observation, Snapshot
from driftctl.core.risk import classify_change

@dataclass
class Anomaly:
    anomaly_type: str
    observation_type: str
    value: str
    risk: str
    reason: str
    baseline: dict | None
    current: dict | None


def build_index(
    observations: list[Observation],
) -> dict[tuple, Observation]:

    return {
        observation_key(observation): observation
        for observation in observations
    }


def detect_anomalies(
    baseline: Baseline,
    snapshot: Snapshot,
) -> list[Anomaly]:

    baseline_index = build_index(
        baseline.observations
    )

    current_index = build_index(
        snapshot.observations
    )

    anomalies = []

    for key, current in current_index.items():

        if key not in baseline_index:

            change = Change(
                change_type="NEW",
                observation_type=current.type,
                value=current.value,
                previous=None,
                current=current.metadata,
            )

            risk, reason = classify_change(
                change
            )

            anomalies.append(
                Anomaly(
                    anomaly_type="NEW",
                    observation_type=current.type,
                    value=current.value,
                    risk=risk,
                    reason=reason,
                    baseline=None,
                    current=current.metadata,
                )
            )

    for key, baseline_observation in baseline_index.items():

        if key not in current_index:

            change = Change(
                change_type="REMOVED",
                observation_type=baseline_observation.type,
                value=baseline_observation.value,
                previous=baseline_observation.metadata,
                current=None,
            )

            risk, reason = classify_change(
                change
            )

            anomalies.append(
                Anomaly(
                    anomaly_type="REMOVED",
                    observation_type=baseline_observation.type,
                    value=baseline_observation.value,
                    risk=risk,
                    reason=reason,
                    baseline=baseline_observation.metadata,
                    current=None,
                )
            )

    for key in baseline_index.keys() & current_index.keys():

        baseline_observation = baseline_index[key]
        current_observation = current_index[key]

        if (
            baseline_observation.metadata
            != current_observation.metadata
        ):

            change = Change(
                change_type="CHANGED",
                observation_type=current_observation.type,
                value=current_observation.value,
                previous=baseline_observation.metadata,
                current=current_observation.metadata,
            )

            risk, reason = classify_change(
                change
            )

            anomalies.append(
                Anomaly(
                    anomaly_type="CHANGED",
                    observation_type=current_observation.type,
                    value=current_observation.value,
                    risk=risk,
                    reason=reason,
                    baseline=baseline_observation.metadata,
                    current=current_observation.metadata,
                )
            )

    return anomalies
