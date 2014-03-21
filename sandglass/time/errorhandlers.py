# pylint: disable=W0613,C0103

import logging

import colander
import sqlalchemy.exc
import transaction

#from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from sandglass.time.api import error
from sandglass.time.resource.base import APIRequestDataError
from sandglass.time.response import error_response

LOG = logging.getLogger(__name__)


@view_config(context=error.APIError)
def handle_api_errors(err, request):
    """
    Generic error handler API errors.

    """
    # Add schema validation information
    data = {
        'code': err.code,
        'details': err.details,
    }
    return error_response(err.msg, data=data)


@view_config(context=colander.Invalid)
def handle_schema_validation_errors(err, request):
    """
    Generic error handler for Colander data and validation errors.

    """
    # Add schema validation information
    data = {
        'code': 'VALIDATION_ERROR',
        'fields': err.asdict(),
        'details': unicode(err),
    }
    message = error.CODES.get(data['code'])
    return error_response(message, data=data)


@view_config(context=sqlalchemy.exc.IntegrityError)
def handle_database_integrity_errors(exc, request):
    """
    Generic error handler for database IntegrityErrors.

    Traceback error message is also added to response.

    """
    # Mark current transaction to be aborted ath the end of request
    transaction.doom()
    # Add exception message to response
    details = exc.message.replace('(IntegrityError)', '')
    data = {
        'code': 'DATA_INTEGRITY_ERROR',
        'details': details.strip(),
    }
    message = error.CODES.get(data['code'])
    return error_response(message, data=data)


@view_config(context=APIRequestDataError)
def handle_api_request_data_errors(err, request):
    """
    Generic error handler for request with invalid JSON data.

    """
    data = {'code': 'INVALID_JSON_DATA'}
    message = error.CODES.get(data['code'])
    return error_response(message, data=data)
