from app.shared.exceptions.base_exceptions import PNCTBaseException


class APIException(PNCTBaseException):
    """Base API exception"""
    pass


class InvalidRequestError(APIException):
    """Invalid request"""
    pass


class UnauthorizedError(APIException):
    """Unauthorized access"""
    pass