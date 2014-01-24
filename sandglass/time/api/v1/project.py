from sandglass.time.api.model import ModelResource
from sandglass.time.models.project import Project


class ProjectResource(ModelResource):
    """
    REST API resource for Project model.

    """
    name = 'projects'
    model = Project
