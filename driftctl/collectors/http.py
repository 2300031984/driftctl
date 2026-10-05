import requests
from bs4 import BeautifulSoup

from driftctl.core.models import Observation


KNOWN_ENDPOINTS = [
    "/",
    "/login",
    "/products",
    "/api/users",
    "/health",
]


def discover_endpoints(
    base_url: str,
) -> list[str]:

    endpoints = set(KNOWN_ENDPOINTS)

    try:
        response = requests.get(
            base_url,
            timeout=5,
            allow_redirects=False,
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for link in soup.find_all("a"):
            href = link.get("href")

            if not href:
                continue

            if href.startswith("/"):
                endpoint = href.split("?")[0]

                if endpoint != "/":
                    endpoints.add(endpoint)

    except requests.RequestException:
        pass

    return sorted(endpoints)


def collect_http(
    base_url: str,
) -> list[Observation]:

    endpoints = discover_endpoints(
        base_url
    )

    observations = []

    for endpoint in endpoints:

        url = base_url.rstrip("/") + endpoint

        try:
            response = requests.get(
                url,
                timeout=5,
                allow_redirects=False,
            )

            observations.append(
                Observation(
                    type="http_endpoint",
                    value=endpoint,
                    metadata={
                        "status_code": response.status_code,
                        "content_type": response.headers.get(
                            "Content-Type",
                            "",
                        ),
                        "server": response.headers.get(
                            "Server",
                            "",
                        ),
                        "content_length": len(
                            response.content
                        ),
                    },
                )
            )

        except requests.RequestException as exc:

            observations.append(
                Observation(
                    type="http_error",
                    value=endpoint,
                    metadata={
                        "error": str(exc),
                    },
                )
            )

    return observations
