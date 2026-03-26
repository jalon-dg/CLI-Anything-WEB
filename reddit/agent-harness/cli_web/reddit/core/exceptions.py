"""Domain-specific exception hierarchy for cli-web-reddit."""


class RedditError(Exception):
    """Base for all Reddit CLI errors."""

    def __init__(self, message: str, code: str = "REDDIT_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error": True, "code": self.code, "message": self.message}


class AuthError(RedditError):
    """401/403 — authentication required or expired."""

    def __init__(self, message: str, recoverable: bool = False):
        self.recoverable = recoverable
        super().__init__(message, "AUTH_EXPIRED")


class RateLimitError(RedditError):
    """429 — retry with backoff."""

    def __init__(self, message: str, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMITED")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["retry_after"] = self.retry_after
        return d


class NetworkError(RedditError):
    """Connection/DNS/timeout errors."""

    def __init__(self, message: str):
        super().__init__(message, "NETWORK_ERROR")


class ServerError(RedditError):
    """5xx responses."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message, "SERVER_ERROR")


class NotFoundError(RedditError):
    """404 — resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class SubmitError(RedditError):
    """Reddit rejected a submit/comment action."""

    def __init__(self, message: str):
        super().__init__(message, "SUBMIT_ERROR")
