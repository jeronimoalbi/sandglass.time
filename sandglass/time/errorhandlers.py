import logging

import colander
import sqlalchemy.exc
import transaction

#from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from sandglass.time import _
from sandglass.time.response import error_response

LOG = logging.getLogger(__name__)


@view_config(context=colander.Invalid)
def handle_schema_validation_errors(err, request):
    """
    Generic error handler for Colander data and validation errors.

    """
    # Add schema validation information
    data = {
        'fields': err.asdict(),
        'message': unicode(err),
    }
    return error_response(_('Submitted data is not valid'), data=data)


@view_config(context=sqlalchemy.exc.IntegrityError)
def handle_integrity_errors(exc, request):
    """
    Generic error handler for database IntegrityErrors.

    Traceback error message is also added to response.

    """
    # Always about transaction because response will be successful
    # and there for transaction manager will try to commit it.
    # TODO: Check if is actually needed. Transaction mgr should handle it.
    transaction.abort()
    # Add exception message to response
    exc_message = exc.message.replace('(IntegrityError)', '')
    data = {'message': exc_message.strip()}
    return error_response(_('Data integrity error'), data=data)
