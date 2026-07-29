from __future__ import annotations


class UMSException(Exception):
    def __init__(self, error: str, message: str, status_code: int = 500):
        self.error = error
        self.message = message
        self.status_code = status_code


class AuthError(UMSException):
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(error="unauthorized", message=message, status_code=401)


class ValidationError(UMSException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(error="validation_error", message=message, status_code=422)


class RateLimitError(UMSException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(error="rate_limited", message=message, status_code=429)


class NotFoundError(UMSException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(error="not_found", message=message, status_code=404)
