class NetworkBotError(Exception):
    """Base exception for all NetworkBot SDK errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(NetworkBotError):
    """Invalid or missing API key."""


class InsufficientCreditsError(NetworkBotError):
    """Agent has run out of credits."""
    def __init__(self, message: str, credits_remaining: float = 0, reset_at: str = ""):
        super().__init__(message, status_code=402)
        self.credits_remaining = credits_remaining
        self.reset_at = reset_at


class NotFoundError(NetworkBotError):
    """Resource not found."""


class RateLimitError(NetworkBotError):
    """Too many requests."""


class ValidationError(NetworkBotError):
    """Invalid request parameters."""
