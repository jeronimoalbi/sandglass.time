from sandglass.time import _
from sandglass.time.api.error import APIError


# API error codes and messages
CODES = {
    'INVALID_SIGNIN': _("Invalid sign in credentials"),
    'USER_EMAIL_EXISTS': _("A user with the same E-Mail already exists"),
    'USER_NOT_FOUND': _("User not found"),
}


class APIV1Error(APIError):
    """
    Exception class for API v1 errors.

    """
    # Dictionary with the error codes to use in this type of exceptions
    codes = CODES
