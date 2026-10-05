from driftctl.core.diff import Change
from driftctl.core.risk import classify_change


def test_authentication_change_is_high():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/api/users",
        previous={
            "status_code": 401
        },
        current={
            "status_code": 200
        },
    )

    risk, reason = classify_change(change)

    assert risk == "HIGH"
    assert "Authentication" in reason


def test_new_admin_endpoint_is_medium():
    change = Change(
        change_type="NEW",
        observation_type="http_endpoint",
        value="/admin",
        previous=None,
        current={
            "status_code": 200
        },
    )

    risk, reason = classify_change(change)

    assert risk == "MEDIUM"
    assert "administrative" in reason


def test_new_api_endpoint_is_medium():
    change = Change(
        change_type="NEW",
        observation_type="http_endpoint",
        value="/api/v2/users",
        previous=None,
        current={
            "status_code": 200
        },
    )

    risk, reason = classify_change(change)

    assert risk == "MEDIUM"
    assert "API" in reason


def test_content_length_change_is_low():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/",
        previous={
            "status_code": 200,
            "content_length": 420
        },
        current={
            "status_code": 200,
            "content_length": 594
        },
    )

    risk, reason = classify_change(change)

    assert risk == "LOW"
    assert "content length" in reason
def test_authentication_requirement_strengthened_is_low():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/api/users",
        previous={
            "status_code": 200
        },
        current={
            "status_code": 401
        },
    )

    risk, reason = classify_change(change)

    assert risk == "LOW"
    assert "200 OK to 401 Unauthorized" in reason


def test_authorization_requirement_strengthened_is_low():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/admin",
        previous={
            "status_code": 200
        },
        current={
            "status_code": 403
        },
    )

    risk, reason = classify_change(change)

    assert risk == "LOW"
    assert "200 OK to 403 Forbidden" in reason
