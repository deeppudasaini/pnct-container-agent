"""Base exception classes"""


class PNCTBaseException(Exception):
    """Base exception for PNCT system"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PNCTBaseException):
    """Validation error"""
    pass


class NotFoundError(PNCTBaseException):
    """Resource not found"""
    pass


class AuthenticationError(PNCTBaseException):
    """Authentication failed"""
    pass


class RateLimitError(PNCTBaseException):
    """Rate limit exceeded"""
    pass