"""Domain-specific exception hierarchy for cli-web-pexels."""


class PexelsError(Exception):
    """Base exception for all Pexels CLI errors."""

    def to_dict(self) -> dict:
        """Return a JSON-serializable error dictionary."""
        return {"error": True, "code": error_code_for(self), "message": str(self)}


class RateLimitError(PexelsError):
    """Server returned 429 — too many requests."""

    def __init__(self, message: str, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message)


class NetworkError(PexelsError):
    """Connection failed — DNS, TCP, TLS, or timeout."""


class ServerError(PexelsError):
    """Server returned 5xx."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(PexelsError):
    """Resource not found (HTTP 404)."""


class ParseError(PexelsError):
    """Failed to parse __NEXT_DATA__ or response HTML."""


EXCEPTION_CODE_MAP = {
    RateLimitError: "RATE_LIMITED",
    NotFoundError: "NOT_FOUND",
    ServerError: "SERVER_ERROR",
    NetworkError: "NETWORK_ERROR",
    ParseError: "PARSE_ERROR",
}


def error_code_for(exc: Exception) -> str:
    """Get the JSON error code string for an exception."""
    for exc_type, code in EXCEPTION_CODE_MAP.items():
        if isinstance(exc, exc_type):
            return code
    return "UNKNOWN_ERROR"
