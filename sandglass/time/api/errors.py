import logging

from sandglass.time import _

LOG = logging.getLogger(__name__)

# API error codes and messages
CODES = {
    'COLLECTION_EXPECTED': _("Submitted data is not a collection"),
    'DATA_INTEGRITY_ERROR': _("Data integrity error"),
    'VALIDATION_ERROR': _("Submitted data is not valid"),
    'OBJECT_NOT_ALLOWED': _(
        "This operation is not allowed for single objects"),
    'COLLECTION_NOT_ALLOWED': _(
        "This operation is not allowed for collections"),
}


class APIError(Exception):
    """
    Exception class for generic API errors.

    Errors are handled by `sandglass.time.errorhandlers.handle_api_errors`.

    """
    default_msg = _("API error")
    # Dictionary with the error codes to use in this type of exceptions
    codes = CODES

    def __init__(self, code, msg=None, details=None):
        super(APIError, self).__init__()
        self.code = code
        self.details = details
        if not msg:
            self.msg = self.codes.get(code)
            # When no message is available use default one
            if not self.msg:
                self.msg = self.default_msg
                LOG.error("API code '%s' is not defined", code)
        else:
            self.msg = msg
