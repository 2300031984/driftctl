from driftctl.core.findings import Finding


def build_explanation(finding: Finding) -> dict:

    explanation = {
        "finding_id": finding.id,
        "target": finding.target,
        "risk": finding.risk,
        "change": {
            "type": finding.change_type,
            "observation_type": finding.observation_type,
            "value": finding.value,
        },
        "reason": finding.reason,
        "security_significance": "",
        "evidence": {
            "previous": finding.previous,
            "current": finding.current,
        },
        "recommendation": "",
        "fingerprint": finding.fingerprint,
        "detected_at": finding.detected_at,
    }

    if (
        finding.change_type == "CHANGED"
        and finding.previous
        and finding.current
    ):

        old_status = finding.previous.get(
            "status_code"
        )

        new_status = finding.current.get(
            "status_code"
        )

        if old_status == 401 and new_status == 200:

            explanation["security_significance"] = (
                "The endpoint changed from requiring "
                "authentication to returning a successful "
                "response to an unauthenticated request. "
                "This may indicate an authentication control "
                "change or unintended exposure."
            )

            explanation["recommendation"] = (
                "Verify that authentication is intentionally "
                "disabled. If authentication is required, "
                "restore the appropriate access control and "
                "test the endpoint with and without valid "
                "credentials."
            )

        elif old_status == 403 and new_status == 200:

            explanation["security_significance"] = (
                "The endpoint changed from denying access "
                "to returning a successful response. "
                "This may indicate an authorization control "
                "change or unintended privilege exposure."
            )

            explanation["recommendation"] = (
                "Verify authorization requirements and "
                "confirm that users without the required "
                "privileges cannot access the endpoint."
            )

        elif (
            old_status is not None
            and new_status is not None
            and old_status < 500
            and new_status >= 500
        ):

            explanation["security_significance"] = (
                "The endpoint transitioned into a server-error "
                "state. This indicates a change in service "
                "behavior and may affect availability."
            )

            explanation["recommendation"] = (
                "Inspect application logs and the deployment "
                "that introduced the change. Determine whether "
                "the server-error state is intentional."
            )

        elif (
            finding.previous.get("content_length")
            != finding.current.get("content_length")
        ):

            explanation["security_significance"] = (
                "The observable response size changed. "
                "This is normally informational and does not "
                "by itself demonstrate a security vulnerability."
            )

            explanation["recommendation"] = (
                "Review the endpoint change if the response "
                "contains security-sensitive functionality "
                "or newly exposed information."
            )

        else:

            explanation["security_significance"] = (
                "Observable HTTP metadata changed. "
                "The change should be reviewed to determine "
                "whether it corresponds to an intentional "
                "application or deployment change."
            )

            explanation["recommendation"] = (
                "Review the deployment or configuration "
                "associated with the endpoint."
            )

    elif finding.change_type == "NEW":

        if finding.value.startswith("/admin"):

            explanation["security_significance"] = (
                "A new administrative endpoint became "
                "externally observable. Administrative "
                "interfaces can represent a higher-value "
                "attack surface."
            )

            explanation["recommendation"] = (
                "Verify that the administrative endpoint is "
                "intentionally exposed and protected by "
                "appropriate authentication and authorization."
            )

        elif finding.value.startswith("/api/"):

            explanation["security_significance"] = (
                "A new API endpoint became externally "
                "observable. APIs can expose application "
                "functionality and data."
            )

            explanation["recommendation"] = (
                "Review the endpoint's authentication, "
                "authorization, input validation, and data "
                "exposure controls."
            )

        else:

            explanation["security_significance"] = (
                "A previously unobserved HTTP endpoint "
                "became externally accessible."
            )

            explanation["recommendation"] = (
                "Confirm that the endpoint is intentionally "
                "public and does not expose sensitive "
                "functionality or information."
            )

    elif finding.change_type == "REMOVED":

        explanation["security_significance"] = (
            "A previously observed asset is no longer "
            "externally observable."
        )

        explanation["recommendation"] = (
            "Confirm that the removal was intentional and "
            "that no replacement endpoint exposes equivalent "
            "functionality."
        )

    else:

        explanation["security_significance"] = (
            "The attack surface changed in a way that "
            "requires contextual review."
        )

        explanation["recommendation"] = (
            "Review the associated deployment or configuration "
            "change."
        )

    return explanation
