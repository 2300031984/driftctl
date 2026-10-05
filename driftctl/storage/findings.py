import json
from pathlib import Path

from driftctl.core.findings import Finding, create_fingerprint
from driftctl.core.diff import Change


FINDING_DIR = Path("data/findings")


def save_finding(finding: Finding) -> Path:
    FINDING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = FINDING_DIR / f"{finding.id}.json"

    path.write_text(
        json.dumps(
            finding.model_dump(mode="json"),
            indent=2,
        )
    )

    return path


def load_finding(
    finding_id: str,
) -> Finding:

    path = FINDING_DIR / f"{finding_id}.json"

    data = json.loads(
        path.read_text()
    )

    return Finding.model_validate(data)


def list_findings() -> list[Path]:

    FINDING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sorted(
        FINDING_DIR.glob("CHANGE-*.json")
    )


def find_by_fingerprint(
    fingerprint: str,
) -> Finding | None:

    for path in list_findings():

        try:
            finding = load_finding(
                path.stem
            )
        except Exception:
            continue

        if finding.fingerprint == fingerprint:
            return finding

    return None


def migrate_legacy_findings() -> list[str]:
    migrated = []

    for path in list_findings():

        try:
            data = json.loads(
                path.read_text()
            )

            change = Change(
                change_type=data["change_type"],
                observation_type=data["observation_type"],
                value=data["value"],
                previous=data.get("previous"),
                current=data.get("current"),
            )

            fingerprint = create_fingerprint(
                change,
                data["target"],
            )

            if data.get("fingerprint") == fingerprint:
                continue

            data["fingerprint"] = fingerprint

            path.write_text(
                json.dumps(
                    data,
                    indent=2,
                )
            )

            migrated.append(path.stem)

        except Exception:
            continue

    return migrated
