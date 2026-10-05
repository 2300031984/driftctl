import hashlib
import json
from datetime import datetime, timezone

from pydantic import BaseModel

from driftctl.core.diff import Change
from driftctl.core.risk import classify_change


class Finding(BaseModel):
    id: str
    fingerprint: str
    target: str
    detected_at: datetime
    change_type: str
    observation_type: str
    value: str
    risk: str
    reason: str
    previous: dict | None = None
    current: dict | None = None


def create_fingerprint(
    change: Change,
    target: str,
) -> str:

    previous = change.previous or {}
    current = change.current or {}

    if change.change_type == "CHANGED":

        old_status = previous.get("status_code")
        new_status = current.get("status_code")

        if old_status == 401 and new_status == 200:
            event = {
                "target": target,
                "type": "AUTHENTICATION_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
                "from": 401,
                "to": 200,
            }
        elif old_status == 200 and new_status == 401:
            event = {
            "target": target,
            "type": "AUTHENTICATION_STRENGTHENED",
            "observation_type": change.observation_type,
            "value": change.value,
            "from": 200,
            "to": 401,
            }

        elif old_status == 200 and new_status == 403:
            event = {
            "target": target,
            "type": "AUTHORIZATION_STRENGTHENED",
            "observation_type": change.observation_type,
            "value": change.value,
            "from": 200,
            "to": 403,
            }

        elif old_status == 403 and new_status == 200:
            event = {
                "target": target,
                "type": "AUTHORIZATION_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
                "from": 403,
                "to": 200,
            }

        elif (
            old_status is not None
            and new_status is not None
            and old_status < 500
            and new_status >= 500
        ):
            event = {
                "target": target,
                "type": "SERVER_ERROR_STATE_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
                "from": old_status,
                "to": new_status,
            }

        elif (
            previous.get("content_length")
            != current.get("content_length")
        ):
            event = {
                "target": target,
                "type": "CONTENT_LENGTH_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
            }

        elif previous.get("server") != current.get("server"):
            event = {
                "target": target,
                "type": "SERVER_FINGERPRINT_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
            }

        else:
            event = {
                "target": target,
                "type": "METADATA_CHANGE",
                "observation_type": change.observation_type,
                "value": change.value,
            }

    elif change.change_type == "NEW":

        event = {
            "target": target,
            "type": "NEW_ASSET",
            "observation_type": change.observation_type,
            "value": change.value,
        }

    elif change.change_type == "REMOVED":

        event = {
            "target": target,
            "type": "REMOVED_ASSET",
            "observation_type": change.observation_type,
            "value": change.value,
        }

    else:

        event = {
            "target": target,
            "type": change.change_type,
            "observation_type": change.observation_type,
            "value": change.value,
        }

    serialized = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def create_finding(
    change: Change,
    target: str,
    finding_id: str,
) -> Finding:

    risk, reason = classify_change(change)

    fingerprint = create_fingerprint(
        change,
        target,
    )

    return Finding(
        id=finding_id,
        fingerprint=fingerprint,
        target=target,
        detected_at=datetime.now(timezone.utc),
        change_type=change.change_type,
        observation_type=change.observation_type,
        value=change.value,
        risk=risk,
        reason=reason,
        previous=change.previous,
        current=change.current,
    )
