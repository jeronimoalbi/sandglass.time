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

    def _get_related_query_mode(self):
        # Dont use query modes when include is missing or when
        # current request is not querying for an object
        if ('include' not in self.request.GET) or not self.pk_value:
            return {}

        include_items = self.request.GET['include'].split(',')
        # Create a dictionary of related field name and query mode
        return dict([item.strip().split(':') for item in include_items])

    @reify
    def is_valid_object(self):
        """
        Check if an object exists for current pk value.

        Return a Boolean.

        """
        query = self.model.query()
        query = query.filter(self.model.id == self.pk_value)
        return (query.count() == 1)

    @reify
    def object(self):
        """
        Get object for current request.

        When check is False dont raise `NotFound` exeption when
        object is not found in database.

        Return a BaseModel instance or None.

        """
        return self._get_object()

    @reify
    def return_fields(self):
        """
        Get a list of field names to return for current model objects.

        Return a List.

        """
        field_names = self.request.params.get('fields')
        if not field_names:
            return []

        return [name.strip() for name in field_names.split(',')]

    @reify
    def related_query_mode(self):
        """
        Get query modes for related objects.

        Supported mode values:
            - full (load all fields; Default one)
            - pk (only load pk values)

        By default no related objects are loaded.

        Loading of related object in the same request is specified
        using a GET parameter called `include`.
        It takes a comma separated list of related objects to load.

        Example:
            include=tags:full,user:pk

        Return a Dictionary.

        """
        # TODO: Implement query/serialization of related objects
        return self._get_related_query_mode()

    @reify
    def submitted_member_data(self):
        """
        Get deserialized data for current member.

        Data is deserialized from current request body.

        Return a Dictionary.

        """
        schema = self.schema()
        return schema.deserialize(self.request_data)

    @reify
    def submitted_collection_data(self):
        """
        Get deserialized data for current collection.

        Data is deserialized from current request body.

        Return a List of dictionaries.

        """
        list_schema = self.list_schema()
        return list_schema.deserialize(self.request_data)

    @transactional
    def post_collection(self, session):
        """
        Create new object(s).

        Request body can be a JSON object or a list of objects.

        """
        is_single_object = isinstance(self.request_data, dict)
        # Get submited JSON data from the request body
        if is_single_object:
            # When POSTed data is an object deserialize it
            # and create a list with this single object
            data_list = [self.submitted_member_data]
        else:
            # By default assume that request data is a list of objects
            data_list = self.submitted_collection_data

        obj_list = []
        for data in data_list:
            obj = self.model(**data)
            session.add(obj)
            obj_list.append(obj)

        # Flush to generate IDs
        session.flush()

        if is_single_object:
            return obj_list[0]
        else:
            return obj_list

    def get_collection(self):
        """
        Get all model objects.

        """
        query = self.model.query()
        if self.return_fields:
            # TODO: Force to always return id field ?
            attributes = self.model.get_attributes_by_name(*self.return_fields)
            return [row._asdict() for row in query.values(*attributes)]
        else:
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
        if self.return_fields:
            if not self.pk_value:
                raise NotFound()

            # Create a query to get the object for current PK value
            query = self.model.query().filter_by(id=self.pk_value)

            attributes = self.model.get_attributes_by_name(*self.return_fields)
            try:
                # Get first result
                row = query.values(*attributes).next()
            except StopIteration:
                raise NotFound()

            # Return a dictionary with result fields
            return row._asdict()
        else:
            return self.object

    def put_member(self):
        """
        Update current object data.

        """
        query = self.object.query()
        try:
            count = query.update(self.submitted_member_data)
        except:
            LOG.exception('Error updating object during PUT request')
            transaction.doom()
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
        return getattr(self.object, self.related_name) or []

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
