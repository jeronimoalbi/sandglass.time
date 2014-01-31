import logging

import transaction

from pyramid.decorator import reify
from pyramid.exceptions import NotFound

from sandglass.time import _
from sandglass.time.api import BaseResource
from sandglass.time.models import transactional
from sandglass.time.response import error_response

LOG = logging.getLogger(__name__)


class ModelResource(BaseResource):
    """
    Base class for REST resources that use a Model to get data.

    """
    model = None

    # Schemas to use for (de)serialization of model data
    schema = None
    list_schema = None

    def _get_object(self, check=True, session=None):
        if not self.model:
            raise Exception('No model assigned to class')

        obj = None
        if self.pk_value:
            obj = self.model.get(self.pk_value, session=session)

        if check and not obj:
            raise NotFound()

        return obj

    @reify
    def object(self):
        """
        Get object for current request.

        When check is False dont raise `NotFound` exeption when
        object is not found in database.

        Return a BaseModel instance or None.

        """
        return self._get_object()

    def handle_rpc_call(self):
        """
        Handle RPC calls for model resources.

        Handlers for specific object call receive the database
        object as argument.

        """
        # When RPC is called for an object, get it and use it
        # as argument for the view handler
        if self.pk_value:
            return self.rpc_handler(self.object)
        else:
            # When RPC is called for a collection dont use arguments
            return self.rpc_handler()

    @transactional
    def post_collection(self, session):
        """
        Create new object(s).

        """
        # Get submited JSON data from the request body
        list_schema = self.list_schema()
        data_list = list_schema.deserialize(self.request.json_body)

        obj_list = []
        for data in data_list:
            obj = self.model(**data)
            session.add(obj)
            obj_list.append(obj)

        # Flush to generate IDs
        session.flush()
        # Generate object dictionaries before commit because after
        # that objects are dettached from the session and then is
        # not possible to read field values from them.
        obj_list = [dict(obj) for obj in obj_list]
        transaction.commit()

        return obj_list

    def get_collection(self):
        """
        Get all model objects.

        """
        query = self.model.query()
        return query.all()

    def delete_collection(self):
        """
        Delete all model objects.

        """
        query = self.model.query()
        count = query.delete()
        # TODO: Return a proper Response instance
        return count

    def get_member(self):
        """
        Get object for current request.

        """
        return self.object

    def put_member(self):
        """
        Update current object data.

        """
        query = self.object.query()
        schema = self.schema()
        data = schema.deserialize(self.request.json_body)
        try:
            count = query.update(data)
        except:
            LOG.exception('Error updating object during PUT request')
            transaction.abort()
            return error_response(_("Object update failed"))

        if not count:
            return error_response(_("No object was updated"))

        return self.object

    def delete_member(self):
        """
        Delete current object from database.

        """
        serialized_object = dict(self.object)
        query = self.object.query()
        count = query.delete()
        if not count:
            return error_response(_('No object was deleted'))
        else:
            # Return the deleted object
            return serialized_object

    def get_related(self):
        """
        Get a list of related objects for current object.

        """
        # TODO: Use count() to avoid useless initial full object query
        #       Raise 404 when object count == 0. Same for delete_related.
        return (getattr(self.object, self.related_name) or [])

    def delete_related(self):
        """
        Delete related objects from current object.

        """
        session = self.object.current_session
        # Get related objects and delete one by one
        # NOTE: They are really deleted during session.flush()
        # TODO: Reimplement using a single delete statement
        related_object_list = getattr(self.object, self.related_name) or ()
        for related_object in related_object_list:
            session.delete(related_object)

        return len(related_object_list)
