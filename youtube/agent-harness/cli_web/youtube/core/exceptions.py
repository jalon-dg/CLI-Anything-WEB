"""Domain exception hierarchy for cli-web-youtube."""


class YouTubeError(Exception):
    """Base for all YouTube CLI errors."""

    def __init__(self, message: str, code: str = "YOUTUBE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error": True, "code": self.code, "message": self.message}


class AuthError(YouTubeError):
    """Authentication required or expired."""

    def __init__(self, message: str = "Authentication required.", recoverable: bool = False):
        self.recoverable = recoverable
        super().__init__(message, "AUTH_EXPIRED")


class RateLimitError(YouTubeError):
    """429 — retry with backoff."""

    def __init__(self, message: str = "Rate limited by YouTube.", retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMITED")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["retry_after"] = self.retry_after
        return d


class NetworkError(YouTubeError):
    """Connection/DNS/timeout errors."""

    def __init__(self, message: str):
        super().__init__(message, "NETWORK_ERROR")


class ServerError(YouTubeError):
    """5xx responses."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message, "SERVER_ERROR")


class NotFoundError(YouTubeError):
    """404 — resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class ParseError(YouTubeError):
    """Failed to parse YouTube response."""

    def __init__(self, message: str = "Failed to parse YouTube response"):
        super().__init__(message, "PARSE_ERROR")
