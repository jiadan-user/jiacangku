from __future__ import annotations

import re


SECRET_ASSIGNMENT_RE = re.compile(
    r"(?P<key>\b(?:token|api[_-]?key|password|passwd|secret|access[_-]?key)\b\s*[:=]\s*)"
    r"(?P<value>[^\s,;]+)",
    re.IGNORECASE,
)
URL_WITH_QUERY_RE = re.compile(r"https?://[^\s)>\]]+\?[^\s)>\]]+")


def redact_text(text: str) -> str:
    """Remove high-risk values while keeping enough context for the memory to be useful."""
    if not text:
        return ""

    def replace_secret(match: re.Match[str]) -> str:
        return f"{match.group('key')}[REDACTED]"

    def replace_url(match: re.Match[str]) -> str:
        url = match.group(0)
        base = url.split("?", 1)[0]
        return f"{base}?[REDACTED]"

    redacted = SECRET_ASSIGNMENT_RE.sub(replace_secret, text)
    redacted = URL_WITH_QUERY_RE.sub(replace_url, redacted)
    return redacted
