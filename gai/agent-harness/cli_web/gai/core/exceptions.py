"""Domain-specific exception hierarchy for cli-web-gai."""


class GAIError(Exception):
    """Base exception for all cli-web-gai errors."""


class BrowserError(GAIError):
    """Browser launch or navigation failure."""


class TimeoutError(GAIError):
    """Response did not arrive within the timeout window."""

    def __init__(self, message: str, timeout_seconds: float = 0):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class RateLimitError(GAIError):
    """Google rate-limiting detected."""


class NetworkError(GAIError):
    """Network or connection failure."""


class ParseError(GAIError):
    """Failed to parse AI Mode response from the page."""


class CaptchaError(GAIError):
    """Google presented a CAPTCHA challenge."""
