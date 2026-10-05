from driftctl.core.diff import Change


def classify_change(change: Change) -> tuple[str, str]:
    """
    Return (risk_level, reason) for a detected change.
    """

    if change.change_type == "NEW":

        if change.observation_type == "http_endpoint":

            if change.value.startswith("/admin"):
                return (
                    "MEDIUM",
                    "New administrative endpoint discovered",
                )

            if change.value.startswith("/api/"):
                return (
                    "MEDIUM",
                    "New API endpoint discovered",
                )

            return (
                "LOW",
                "New HTTP endpoint discovered",
            )

        return (
            "LOW",
            "New observable asset discovered",
        )

    if change.change_type == "REMOVED":

        return (
            "LOW",
            "Previously observed asset is no longer present",
        )

    if change.change_type == "CHANGED":

        previous = change.previous or {}
        current = change.current or {}

        old_status = previous.get("status_code")
        new_status = current.get("status_code")

        # Authentication/access-control behavior changed.
        if old_status == 401 and new_status == 200:
            return (
                "HIGH",
                "Authentication/access behavior changed from "
                "401 Unauthorized to 200 OK",
            )

        if old_status == 403 and new_status == 200:
            return (
                "HIGH",
                "Authorization behavior changed from "
                "403 Forbidden to 200 OK",
            )
        if old_status == 200 and new_status == 401:
            return (
                "LOW",
                "Authentication/access behavior changed from "
                "200 OK to 401 Unauthorized",
            )

        if old_status == 200 and new_status == 403:
            return (
                "LOW",
                "Authorization behavior changed from "
                "200 OK to 403 Forbidden",
            )

        # Endpoint became unavailable.
        if (
            old_status is not None
            and new_status is not None
            and old_status < 500
            and new_status >= 500
        ):
            return (
                "MEDIUM",
                "HTTP endpoint changed from available to server-error state",
            )

        # HTTP status changed in general.
        if old_status != new_status:
            return (
                "MEDIUM",
                f"HTTP status changed from {old_status} to {new_status}",
            )

        # Content changed while the HTTP behavior remained the same.
        if previous.get("content_length") != current.get(
            "content_length"
        ):
            return (
                "LOW",
                "HTTP response content length changed",
            )

        if previous.get("server") != current.get("server"):
            return (
                "LOW",
                "Server technology fingerprint changed",
            )

        return (
            "LOW",
            "Observable endpoint metadata changed",
        )

    return (
        "LOW",
        "Unclassified change",
    )
