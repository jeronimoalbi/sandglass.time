import logging

import colander
import sqlalchemy.exc
import transaction

#from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from sandglass.time import _
from sandglass.time.api import APIRequestDataError
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
def handle_database_integrity_errors(exc, request):
    """
    Generic error handler for database IntegrityErrors.

    Traceback error message is also added to response.

    """
    # Mark current transaction to be aborted ath the end of request
    transaction.doom()
    # Add exception message to response
    exc_message = exc.message.replace('(IntegrityError)', '')
    data = {'message': exc_message.strip()}
    return error_response(_('Data integrity error'), data=data)


@view_config(context=APIRequestDataError)
def handle_api_request_data_errors(err, request):
    """
    Generic error handler for request with invalid JSON data.

    """
    return error_response(_('Request contains invalid JSON data'))
