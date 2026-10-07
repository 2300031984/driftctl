from urllib.parse import urlparse


def normalize_target(target: str) -> str:
    target = target.strip()

    if not target:
        raise ValueError("Target cannot be empty")

    if "://" not in target:
        target = f"http://{target}"

    parsed = urlparse(target)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError(
            "Target must use http:// or https://"
        )

    if not parsed.netloc:
        raise ValueError(
            "Target must contain a valid hostname"
        )

    return target.rstrip("/")


def get_scan_domain(target: str) -> str:
    normalized = normalize_target(target)

    hostname = urlparse(normalized).hostname

    if not hostname:
        raise ValueError(
            "Unable to determine hostname from target"
        )

    parts = hostname.split(".")

    if len(parts) < 2:
        return hostname

    return ".".join(parts[-2:])
