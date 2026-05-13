class AppBaseException(Exception):
    """Base class for exceptions in bot"""
    pass


class ResourceNotFoundError(AppBaseException):
    """Resource not found in backend (404)"""
    pass


class BackendServerError(AppBaseException):
    """Backend error (50x errors)"""
    pass


class ValidationError(AppBaseException):
    """Invalid request error (422)"""
    pass


class NotAuthorizedError(AppBaseException):
    """User not authorized error (401, 403)"""
    pass


class NetworkConnectionError(AppBaseException):
    """Connection lost error"""
    pass
