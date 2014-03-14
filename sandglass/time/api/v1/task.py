from sandglass.time.models.task import Task
from sandglass.time.resource.model import ModelResource
from sandglass.time.schemas.task import TaskListSchema
from sandglass.time.schemas.task import TaskSchema


class TaskResource(ModelResource):
    """
    REST API resource for Task model.

    """
    name = 'tasks'
    model = Task
    schema = TaskSchema
    list_schema = TaskListSchema
