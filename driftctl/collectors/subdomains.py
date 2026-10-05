import subprocess

from driftctl.core.models import Observation


def collect_subdomains(target: str) -> list[Observation]:
    result = subprocess.run(
        ["subfinder", "-d", target, "-silent"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    observations = []

    for line in result.stdout.splitlines():
        subdomain = line.strip()

        if not subdomain:
            continue

        observations.append(
            Observation(
                type="subdomain",
                value=subdomain,
                metadata={
                    "source": "subfinder"
                },
            )
        )

    return observations
