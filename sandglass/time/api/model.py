import logging

from functools import wraps

import transaction

from pyramid.decorator import reify
from pyramid.exceptions import NotFound
from sqlalchemy.orm import joinedload

from sandglass.time import _
from sandglass.time.api import BaseResource
from sandglass.time.api.errors import APIError
from sandglass.time.filters import QueryFilterError
from sandglass.time.models import BaseModel
from sandglass.time.models import transactional
from sandglass.time.response import error_response
from sandglass.time.response import info_response


LOG = logging.getLogger(__name__)


# TODO: Implement a serializer for collections
class ResourceSerializerProxy(object):
    """
    Class definition to handle serialization of BaseModel objects.

    This class handles loading of related resources.

    """
    def __init__(self, resource, obj):
        self.resource = resource
        self.obj = obj

    def __json__(self, request):
        return self.serialize()

    def serialize(self):
        """
        Get current object serialized.

        Returns a Dictionary.

        """
        data = dict(self.obj)
        if self.resource.related_query_mode:
            data = self.load_related_data(data)

        return data

    def load_related_data(self, data):
        """
        Load related field values into data dictionary.

        Returns a Dictionary.

        """
        for field_name, mode in self.resource.related_query_mode.items():
            # Skip non existing or private fields
            is_private = field_name.startswith('_')
            if is_private or not self.obj.has_field(field_name):
                continue

            field_value = getattr(self.obj, field_name, None)
            data[field_name] = self.parse_value(field_value, mode, field_name)

        return data

    def parse_value(self, value, mode, field_name):
        if not value:
            return value
        elif isinstance(value, BaseModel):
            if mode == 'pk':
                return value.id
            else:
                return dict(value)
        elif isinstance(value, list):
            return [self.parse_value(item, mode, field_name) for item in value]
        else:
            msg = ("Related value %s for field %s.%s is not an"
                   "instance of BaseModel or a list of BaseModel")
            LOG.error(msg, value, self.obj.__class__.__name__, field_name)


def use_schema(schema):
    """
    ModelResource decorator to change the schema for a method call.

    """
    def inner_use_schema(func):
        @wraps(func)
        def wrapper_use_schema(self, *args, **kwargs):
            # Save original schema before asigning the new one
            self.cls_schema = self.schema
            self.schema = schema

            return func(self, *args, **kwargs)

        return wrapper_use_schema

    return inner_use_schema


def handle_collection_rest_modes(func):
    """
    Method decorator that handles results for collection requests.

    When request contains a collection, and result is a single object,
    it is returned as an object when REST collection mode is 'permissive',
    otherwise it is returned as a list with a single object to comply
    with REST specifications for collection requests.

    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        # When result is a list and a single object was submitted
        # check if "permissive" mode is enabled for rest requests
        # and if so return a single object instead of a collection.
        request = self.request
        is_collection_result = isinstance(result, list)
        is_permissive = (request.rest_collection_mode == 'permissive')
        if is_collection_result and is_permissive and request.is_member:
            return result[0]

        return result

    return wrapper


class ModelResource(BaseResource):
    """
    Base class for REST resources that use a Model to get data.

    """
    model = None

    # Serialization class to use for converting model
    # and list of model resources to a dictionary
    serializer_cls = ResourceSerializerProxy

    # Schemas to use for (de)serialization of model data
    schema = None
    list_schema = None

    # N-Tuple of QueryFilter to apply to current model query
    query_filters = None

    # Modes used to load related member data
    related_query_modes = ('pk', 'full')

    @classmethod
    def _get_model_relationships(cls):
        return cls.model.__mapper__.relationships

    def _get_related_name(self):
        related_name = super(ModelResource, self)._get_related_name()
        # Check that related name is in fact a relationship
        if related_name:
            if related_name not in self._get_model_relationships():
                raise NotFound()

        return related_name

    def _get_object(self, check=True, session=None):
        if not self.model:
            raise Exception('No model assigned to class')

        obj = None
        if self.pk_value:
            query = self.get_model_query(session=session)
            obj = query.first()

        if check and not obj:
            raise NotFound()

        return obj

    def _get_related_query_mode(self, default_mode='pk'):
        """
        Get a dictionary of related field name and query mode.

        Returns a Dictionary.

        """
        query_modes = {}
        params = self.request.GET
        include_list = params.getall('inc') + params.getall('include')
        if not include_list:
            return query_modes

        # TODO: Make query modes work with POST requests ??
        for item in include_list:
            if '__' in item:
                try:
                    (field_name, mode) = item.split('__')
                except ValueError:
                    # Skip invalid include values
                    continue
            else:
                field_name = item
                mode = default_mode

            # Skip field when mode is invalid
            if mode not in self.related_query_modes:
                msg = "Invalid related query mode %s for field %s"
                LOG.warning(msg, mode, field_name)
                continue

            query_modes[field_name] = mode

        return query_modes

    @reify
    def is_valid_object(self):
        """
        Check if an object exists for current pk value.

        Return a Boolean.

        """
        query = self.model.query()
        query = query.filter(self.model.id == self.pk_value)
        return query.count() == 1

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

        fields = [name.strip() for name in field_names.split(',')]
        # Always return the ID value
        if 'id' not in fields:
            fields.insert(0, 'id')

        return fields

    @reify
    def related_query_mode(self):
        """
        Get query modes for related objects.

        Supported mode values:
            - full (load all fields)
            - pk (only load pk values)

        By default no related objects are loaded.
        When no mode is given then `pk` is used as default.

        Loading of related object in the same request is specified
        using a GET parameter called `include` or `inc`.
        It takes a single related object name to load; To load more
        than one related object use many times the include parameter.

        Example:
            include=tags__full&inc=user__pk&include=groups__pk

        Return a Dictionary.

        """
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

        When submitted data is a single member, it is deserialized
        and returned as a single object in a list when REST collection
        mode is not 'strict'. By default mode is 'default'.

        Return a List of dictionaries.

        """
        # Conver single object to a list when 'strict' mode is off,
        # if not treat request data as a collection/list.
        strict_mode_off = (self.request.rest_collection_mode != 'strict')
        if strict_mode_off and self.request.is_member:
            # When POSTed data is an object deserialize it
            # and create a list with this single object
            return [self.submitted_member_data]
        else:
            if not isinstance(self.request_data, list):
                raise APIError('COLLECTION_EXPECTED')

            list_schema = self.list_schema()
            return list_schema.deserialize(self.request_data)

    def get_query_filters(self):
        """
        Get query filters for current resource.

        Return an N-Tuple of QueryFilter.

        """
        return self.query_filters

    def apply_model_query_filters(self, query_filters, query):
        """
        Apply a list of QueryFilter to a Query.

        Filters are applied sequentially.

        Returns a Query.

        """
        resource = self
        for filter_ in query_filters:
            if not filter_.applies_to(resource):
                continue

            query = filter_.filter_query(query, self.request, resource)

        return query

    def get_model_query(self, session=None):
        """
        Get a query for current model.

        When request is a member request, query filter results for current
        member PK value.

        Related query modes are also processed and added to query.

        Returns a Query.

        """
        relationships = self._get_model_relationships()
        # Initialize loading options for included related fields
        load_options = []
        for field_name, mode in self.related_query_mode.items():
            if field_name not in relationships:
                msg = "Field %s does not exist in model %s"
                LOG.debug(msg, field_name, self.model.__class__.__name__)
                continue

            load_mode = joinedload(field_name)
            if mode == 'pk':
                # Only load PK field values in model query
                load_mode = load_mode.load_only('id')

            load_options.append(load_mode)

        # When request is made to get a related value from a member
        # add a joinedload for that field to avoid another query
        if self.related_name:
            load_mode = joinedload(self.related_name)
            load_options.append(load_mode)

        # Create the base model query
        query = self.model.query(session=session)
        if self.is_member_request:
            query = query.filter_by(id=self.pk_value)

        # Apply model query filters
        query_filters = self.get_query_filters()
        if query_filters:
            try:
                query = self.apply_model_query_filters(query_filters, query)
            except QueryFilterError, err:
                raise APIError('INVALID_FILTER', details=err.message)

        # Add load options
        if load_options:
            query = query.options(*load_options)

        return query

    @handle_collection_rest_modes
    @transactional
    def post_collection(self, session):
        """
        Create new object(s).

        Request body can be a JSON object or a list of objects.

        """
        obj_list = []
        for data in self.submitted_collection_data:
            obj = self.model(**data)
            session.add(obj)
            obj_list.append(obj)

        # Flush to generate IDs
        try:
            session.flush()
        except:
            msg = "Unable to flush POST collectiond data for /%s"
            LOG.exception(msg, self.get_route_prefix())
            return error_response(_("Error creating object(s)"))

        return obj_list

    @transactional
    def put_collection(self, session):
        """
        Update one or multiple objects.

        Each object MUST contain its original pk value.

        """
        data_list = self.submitted_collection_data
        # Update all members in data list
        count = 0
        query = session.query(self.model)
        try:
            for data in data_list:
                pk_value = data.pop('id')
                update_query = query.filter(self.model.id == pk_value)
                update_query.update(data)
                count += 1
        except:
            LOG.exception('Error updating object(s) during PUT request')
            transaction.doom()
            return error_response(_("Object(s) update failed"))

        if not count:
            return error_response(_("No object(s) updated"))

        msg = _("Object(s) updated successfully")
        # TODO: Check support for rowcount
        # http://docs.sqlalchemy.org/en/latest/core/connections.html
        #                             #sqlalchemy.engine.ResultProxy.rowcount
        return info_response(msg, data={'count': count})

    def get_collection(self):
        """
        Get all model objects.

        """
        collection = []
        query = self.get_model_query()
        object_list = query.all()
        if self.return_fields:
            for obj in object_list:
                serializer = self.serializer_cls(self, obj)
                member = serializer.serialize()
                # Remove fields that are not needed from member
                for field_name in member.keys():
                    if field_name not in self.return_fields:
                        del member[field_name]

                collection.append(member)
        else:
            for obj in object_list:
                serializer = self.serializer_cls(self, obj)
                collection.append(serializer)

        return collection

    def delete_collection(self):
        """
        Delete all model objects.

        """
        id_list = [data['id'] for data in self.submitted_collection_data]
        query = self.model.query().filter(self.model.id.in_(id_list))
        count = query.delete(False)

        if not count:
            msg = _("No objects were deleted")
        else:
            msg = _("Object(s) deleted successfully")

        return info_response(msg, data={'count': count})

    def get_member(self):
        """
        Get object for current request.

        """
        obj = self.object
        if self.return_fields:
            serializer = self.serializer_cls(self, obj)
            member = serializer.serialize()
            # Remove fields that are not needed from member
            for field_name in member.keys():
                if field_name not in self.return_fields:
                    del member[field_name]

            # Return a dictionary only with requested fields
            return member
        else:
            return self.serializer_cls(self, obj)

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
        related = getattr(self.object, self.related_name) or []
        if related is None:
            return
        elif not isinstance(related, list):
            # Return a single object
            return self.serializer_cls(self, related)

        # When related is a list serialize each object
        collection = []
        for obj in related:
            serializer = self.serializer_cls(self, obj)
            collection.append(serializer)

        return collection

    def _get_submitted_related_id_list(self):
        # Get IDs for the related members to remove
        if self.request.is_collection:
            request_data = self.request.json_body
        elif self.request.is_member:
            raise APIError('OBJECT_NOT_ALLOWED')
        else:
            # Request body contains invalid data
            raise APIError('VALIDATION_ERROR')

        # Get ID values for the related object(s)
        id_list = []
        for item in request_data:
            # Each submitted item must be an object or an integer.
            # When is an object it has to contain an 'id' field,
            # else it has to be the value of an object ID.
            if not isinstance(item, (dict, int)):
                raise APIError('VALIDATION_ERROR')

            is_dict = isinstance(item, dict)
            item_id = (item.get('id') if is_dict else item)
            if not item_id:
                LOG.error("Item %s does not have an ID value", item)
                continue
            else:
                id_list.append(item_id)

        return id_list

    def put_related(self):
        """
        Update related object collection.

        Update is only allowed for related objects that are collections.

        When an object or list of objects is submitted, the only needed
        mandatory field is the `id` field; All other fields are ignored.

        A request could contain a list of objects:

            [{'id': 1, ..}, {'id': 99, ..}, ..]

        or a list of integers:

            [1, 99, ..]

        """
        related = getattr(self.object, self.related_name)
        model_relationships = self._get_model_relationships()
        relationship = model_relationships[self.related_name]
        # Check that relationship is using a list and not a single object
        if not relationship.uselist:
            raise APIError('OBJECT_NOT_ALLOWED')

        # Create a query to get related objects to be appended
        update_id_list = self._get_submitted_related_id_list()
        related_class = relationship.mapper.class_
        query = related_class.query(session=self.object.current_session)
        query = query.filter(related_class.id.in_(update_id_list))
        # Add related objects to current member
        count = 0
        for obj in query.all():
            related.append(obj)
            count += 1

        msg = _("Object(s) added successfully")
        return info_response(msg, data={'count': count})

    def delete_related(self):
        """
        Remove related objects from current object.

        Removal is only allowed for related objects that are collections.

        When an object or list of objects is submitted, the only needed
        mandatory field is the `id` field; All other fields are ignored.

        A request could contain a list of objects:

            [{'id': 1, ..}, {'id': 99, ..}, ..]

        or a list of integers:

            [1, 99, ..]

        """
        related = getattr(self.object, self.related_name, None)
        if not related:
            return info_response(_("Nothing to delete"), data={'count': 0})
        elif not isinstance(related, list):
            raise APIError('OBJECT_NOT_ALLOWED')
        else:
            # Related is a collection of objects
            related_list = related
            remove_id_list = self._get_submitted_related_id_list()
            count = 0
            for obj in related_list[:]:
                if obj.id in remove_id_list:
                    related_list.remove(obj)
                    count += 1

            msg = _("Object(s) deleted successfully")
            return info_response(msg, data={'count': count})
