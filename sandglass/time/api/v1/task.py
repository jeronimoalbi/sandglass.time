from sandglass.time.api.model import ModelResource
from sandglass.time.models.task import Task


class TaskResource(ModelResource):
    """
    REST API resource for Task model.

    """
    name = 'tasks'
    model = Task
