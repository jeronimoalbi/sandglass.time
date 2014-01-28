import transaction

from colander import Invalid
from sqlalchemy.exc import IntegrityError
from pyramid.exceptions import NotFound

from sandglass.time.api import BaseResource
from sandglass.time.models import transactional


class ModelResource(BaseResource):
    """
    Base class for REST resources that use a Model to get data.

    """
    model = None

    # Schemas to use for (de)serialization of model data
    schema = None
    list_schema = None

    def get_pk_value(self):
        """
        Get primary key value for current request.

        Return an Integer or None.

        """
        value = self.request.matchdict.get('pk')
        try:
            pk_value = int(value)
        except ValueError:
            pk_value = None

        return pk_value

    def get_object(self, check=True):
        """
        Get object for current request.

        When check is False dont raise `NotFound` exeption when
        object is not found in database.

        Return a BaseModel instance or None.

        """
        if not self.model:
            raise Exception('No model assigned to class')

        pk_value = self.get_pk_value()
        obj = self.model.get(pk_value)
        if check and not obj:
            raise NotFound()

        return obj

    def before_session_add(self, obj):
        """
        Called after a new object is created.

        """

    @transactional
    def post_all(self, session):
        """
        Create new object(s).

        """
        # Get submited JSON data from the request body
        list_schema = self.list_schema()
        try:
            users_data_list = list_schema.deserialize(self.request.json_body)
        except Invalid as err:
            transaction.abort()
            # TODO: Log invalid exceptions
            # TODO: return proper error response
            return unicode(err)

        obj_list = []
        for data in users_data_list:
            obj = self.model(**data)
            self.before_session_add(obj)
            session.add(obj)
            obj_list.append(obj)

        try:
            # Flush users to generate IDs
            session.flush()
            # Generate object dictionaries here because after commit
            # objects are dettached from the session and then is
            # not possible to read field values.
            obj_list = [dict(obj) for user in obj_list]

            transaction.commit()
        except IntegrityError as err:
            transaction.abort()
            # TODO: return proper error response
            return err.message

        return obj_list

    def get_all(self):
        """
        Get all user objects.

        """
        query = self.model.query()
        return query.all()

    def delete_all(self):
        """
        Delete all user objects.

        """
        query = self.model.query()
        count = query.delete()

        # TODO: Return a proper Response instance
        return count

    def get(self):
        """
        Get user object for current `pk` value.

        """
        return self.get_object()

    @transactional
    def put(self, session):
        """
        Update object data.

        """
        obj = self.get_object()
        schema = self.schema()
        try:
            user_data = schema.deserialize(self.request.json_body)
        except Invalid as err:
            transaction.abort()
            # TODO: Log invalid exceptions
            # TODO: return proper error response
            return unicode(err)

        try:
            query = obj.query(session=session)
            count = query.update(user_data)
        # TODO: Handle errors during update
        except:
            transaction.abort()
            # TODO: return proper error response
            return "Object update failed"

        if not count:
            # TODO: return proper error response
            return "No object was updated"

        return obj

    @transactional
    def delete(self, session):
        """
        Delete current object from database.

        """
        obj = self.get_object()
        query = obj.query(session=session)
        count = query.delete()
        
        if count != 1:
            # TODO:  Return a proper Error Response 
            return count
        else:
            # TODO:  Return a proper Response instance
            return True

    # TODO: Implement related methods
