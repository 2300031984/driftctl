from driftctl.core.diff import Change
from driftctl.core.findings import create_fingerprint


def test_authentication_strengthened_fingerprint_is_semantic():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/api/users",
        previous={
            "status_code": 200,
            "content_length": 100,
        },
        current={
            "status_code": 401,
            "content_length": 150,
        },
    )

    fingerprint = create_fingerprint(
        change,
        "test",
    )

    assert fingerprint


def test_authorization_strengthened_fingerprint_is_semantic():
    change = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/admin",
        previous={
            "status_code": 200,
        },
        current={
            "status_code": 403,
        },
    )

    fingerprint = create_fingerprint(
        change,
        "test",
    )

    assert fingerprint


def test_semantic_fingerprint_ignores_unrelated_metadata():
    first = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/api/users",
        previous={
            "status_code": 200,
            "content_length": 100,
            "server": "Werkzeug",
        },
        current={
            "status_code": 401,
            "content_length": 150,
            "server": "Werkzeug",
        },
    )

    second = Change(
        change_type="CHANGED",
        observation_type="http_endpoint",
        value="/api/users",
        previous={
            "status_code": 200,
            "content_length": 999,
            "server": "OtherServer",
        },
        current={
            "status_code": 401,
            "content_length": 300,
            "server": "OtherServer",
        },
    )

    assert create_fingerprint(
        first,
        "test",
    ) == create_fingerprint(
        second,
        "test",
    )
