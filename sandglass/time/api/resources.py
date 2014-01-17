"""API Resources

"""
from cornice.resource import resource
from cornice.resource import view

from sandglass.time.api import BaseAPIResource
# from sandglass.time.models.activity import Activity
from sandglass.time.models.client import Client
from sandglass.time.models.project import Project
from sandglass.time.models.tag import Tag
from sandglass.time.models.task import Task


# TODO: temp DB dict for testing
_DB = {
    'activities': {},
    'clients': {},
    'projects': {},
    'tags': {},
    'tasks': {},
    }


@resource(path='/activity/{id}', collection_path='/activities')
class ActivityResource(BaseAPIResource):

    def collection_get(self):
        """Return a list of activities"""
        return {'activities': _DB['activities'].keys()}

    def get(self):
        return _DB['activities'].get(int(self.request.matchdict['id']))

    def post(self):
        key = self.request.matchdict['activities']
        try:
            _DB['activities'][key] = json.loads(self.request.body)
        except ValueError:
            return False
        print _DB
        return True


@resource(collection_path='/clients', path='/clients/{id}')
class ClientResource(BaseAPIResource):

    def collection_get(self):
        return {'clients': _DB['clients'].keys()}

    @view(renderer='json')
    def get(self):
        return _DB['clients'].get(int(self.request.matchdict['id']))

    @view(renderer='json')
    def post(self):
        return True


@resource(collection_path='/projects', path='/project/{id}')
class ProjectResource(BaseAPIResource):

    def collection_get(self):
        return {'projects': _DB['projects'].keys()}

    @view(renderer='json')
    def get(self):
        return _DB['projects'].get(int(self.request.matchdict['id']))

    @view(renderer='json')
    def post(self):
        return True


@resource(collection_path='/tags', path='/tag/{id}')
class TagResource(BaseAPIResource):

    def collection_get(self):
        return {'tags': _DB['tags'].keys()}

    @view(renderer='json')
    def get(self):
        return _DB['tags'].get(int(self.request.matchdict['id']))

    @view(renderer='json')
    def post(self):
        return True


@resource(collection_path='/tasks', path='/tasks/{id}')
class TaskResource(BaseAPIResource):

    def collection_get(self):
        """Return a list of tasks"""
        return {'tasks': _DB['tasks'].keys()}

    @view(renderer='json')
    def get(self):
        """Return Task by id """
        # TODO
        # get db session
        # query db for task id
        # return Task
        return _DB.get(int(self.request.matchdict['id']))

    @view(renderer='json')
    def post(self):
        return True

