from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
import re
import requests
from bs4 import BeautifulSoup

from driftctl.core.models import Observation
from driftctl.core.target import normalize_target


MAX_PAGES = 50
REQUEST_TIMEOUT = 5

from pathlib import PurePosixPath

STATIC_EXTENSIONS = {
    ".js",
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
    ".pdf",
}

JS_PATH_PATTERN = re.compile(
    r"""["'`](\/(?:api|ajax|index\.php|admin|auth|login|user|users|profile|dashboard|employee|employees|service|services|upload|download|search|report|reports|data|v1|v2)[^"'`\\\s]*)["'`]""",
    re.IGNORECASE,
)


def normalize_endpoint(path: str) -> str:
    """
    Normalize a discovered endpoint.
    """

    path = path.strip()

    if not path:
        return "/"

    if not path.startswith("/"):
        path = f"/{path}"

    return path


def classify_endpoint(path: str) -> str:
    """
    Classify a discovered HTTP resource.
    """

    suffix = PurePosixPath(
        path.split("?", 1)[0]
    ).suffix.lower()

    if suffix in STATIC_EXTENSIONS:
        return "static_asset"

    return "http_endpoint"

def extract_js_endpoints(
    javascript: str,
) -> set[str]:
    """
    Extract obvious application paths from JavaScript.

    JavaScript is parsed as text only.
    No JavaScript is executed.
    """

    endpoints = set()

    for match in JS_PATH_PATTERN.finditer(
        javascript
    ):
        endpoint = match.group(1)

        if endpoint:
            endpoints.add(
                normalize_endpoint(endpoint)
            )

    return endpoints

def normalize_endpoint(path: str) -> str:
    """
    Normalize an endpoint while preserving meaningful query parameters.
    """

    path = path.strip()

    if not path:
        return "/"

    if not path.startswith("/"):
        path = f"/{path}"

    return path

def normalize_url(url: str, base_url: str) -> str | None:
    """Normalize a discovered URL and keep it HTTP(S)."""

    url = url.strip()

    if not url:
        return None

    absolute = urljoin(base_url, url)
    absolute, _ = urldefrag(absolute)

    parsed = urlparse(absolute)

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return absolute.rstrip("/") or absolute


def is_same_origin(url: str, base_url: str) -> bool:
    """Allow crawling only the original host."""

    target = urlparse(url)
    base = urlparse(base_url)

    return (
        target.scheme == base.scheme
        and target.netloc == base.netloc
    )


def discover_metadata_files(
    base_url: str,
) -> set[str]:
    """
    Discover endpoints referenced by robots.txt
    and sitemap.xml.
    """

    discovered = set()

    metadata_urls = [
        f"{base_url}/robots.txt",
        f"{base_url}/sitemap.xml",
    ]

    for metadata_url in metadata_urls:

        try:
            response = requests.get(
                metadata_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )

        except requests.RequestException:
            continue

        if response.status_code != 200:
            continue

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        # robots.txt
        if metadata_url.endswith(
            "/robots.txt"
        ):
            for line in response.text.splitlines():

                line = line.strip()

                if not line.lower().startswith(
                    "sitemap:"
                ):
                    continue

                sitemap_url = line.split(
                    ":",
                    1,
                )[1].strip()

                normalized = normalize_url(
                    sitemap_url,
                    base_url,
                )

                if normalized and is_same_origin(
                    normalized,
                    base_url,
                ):
                    discovered.add(
                        urlparse(normalized).path
                        or "/"
                    )

        # sitemap.xml
        elif (
            metadata_url.endswith(
                "/sitemap.xml"
            )
            and (
                "xml" in content_type
                or response.text.lstrip().startswith(
                    "<?xml"
                )
            )
        ):
            soup = BeautifulSoup(
                response.text,
                "xml",
            )

            for location in soup.find_all(
                "loc"
            ):
                value = location.get_text(
                    strip=True
                )

                normalized = normalize_url(
                    value,
                    base_url,
                )

                if not normalized:
                    continue

                if not is_same_origin(
                    normalized,
                    base_url,
                ):
                    continue

                parsed = urlparse(
                    normalized
                )

                endpoint = normalize_endpoint(
                    parsed.path or "/"
                )

                if parsed.query:
                    endpoint += (
                        f"?{parsed.query}"
                    )

                discovered.add(endpoint)

    return discovered

def discover_endpoints(base_url: str) -> list[str]:
    """
    Crawl same-origin pages and discover internal endpoints.
    Also extracts obvious application paths from JavaScript files.
    """

    base_url = normalize_target(base_url)

    queue = deque([base_url])
    visited = set()
    discovered = set()

    discovered.update(
        discover_metadata_files(base_url)
    )

    while queue and len(visited) < MAX_PAGES:

        current_url = queue.popleft()

        normalized = normalize_url(
            current_url,
            base_url,
        )

        if not normalized:
            continue

        if normalized in visited:
            continue

        if not is_same_origin(
            normalized,
            base_url,
        ):
            continue

        visited.add(normalized)

        try:
            response = requests.get(
                normalized,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )

        except requests.RequestException:
            continue

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        parsed = urlparse(normalized)

        endpoint = normalize_endpoint(
            parsed.path or "/"
        )

        if parsed.query:
            endpoint += f"?{parsed.query}"

        discovered.add(endpoint)

        # -------------------------------------------------
        # JavaScript endpoint extraction
        # -------------------------------------------------

        if (
            "javascript" in content_type
            or normalized.lower().endswith(".js")
        ):
            js_endpoints = extract_js_endpoints(
                response.text
            )

            for js_endpoint in js_endpoints:
                discovered.add(js_endpoint)

            continue

        # -------------------------------------------------
        # Only parse HTML documents
        # -------------------------------------------------

        if "text/html" not in content_type:
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup.find_all(
            ["a", "form", "script"]
        ):

            if tag.name == "a":
                attribute = "href"

            elif tag.name == "form":
                attribute = "action"

            else:
                attribute = "src"

            value = tag.get(attribute)

            if not value:
                continue

            discovered_url = normalize_url(
                value,
                normalized,
            )

            if not discovered_url:
                continue

            if not is_same_origin(
                discovered_url,
                base_url,
            ):
                continue

            discovered_endpoint = normalize_endpoint(
                urlparse(discovered_url).path or "/"
            )

            discovered.add(
                discovered_endpoint
            )

            if discovered_url not in visited:
                queue.append(
                    discovered_url
                )

    return sorted(discovered)

def collect_http(
    base_url: str,
) -> list[Observation]:

    base_url = normalize_target(base_url)

    endpoints = discover_endpoints(
        base_url
    )

    observations = []

    for endpoint in endpoints:

        url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )

            observations.append(
                Observation(
                    type=classify_endpoint(endpoint),
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
