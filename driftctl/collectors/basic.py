from driftctl.core.models import Observation


def collect_basic(target: str) -> list[Observation]:
    return [
        Observation(
            type="target",
            value=target,
        )
    ]
