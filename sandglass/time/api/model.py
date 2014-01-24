from pyramid.exceptions import NotFound

from sandglass.time.api import BaseResource


class ModelResource(BaseResource):
    """
    Base class for REST resources that use a Model to get data.

    """
    model = None

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

    def post_all(self):
        """
        Create new user(s).

        """
        # TODO: Implement

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

    def put(self):
        """
        Update object data.

        """
        # TODO: Implement

    def delete(self):
        """
        Delete current object from database.

        """
        obj = self.get_object()
        obj.delete()

        # TODO:  Return a proper Response instance
        return True

    # TODO: Implement related methods
