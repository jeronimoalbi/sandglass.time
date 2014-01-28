from sandglass.time.api.model import ModelResource
from sandglass.time.forms.task import TaskListSchema
from sandglass.time.forms.task import TaskSchema
from sandglass.time.models.task import Task


class TaskResource(ModelResource):
    """
    REST API resource for Task model.

    """
    name = 'tasks'
    model = Task
    schema = TaskSchema
    list_schema = TaskListSchema
