from sqlalchemy import or_

from sandglass.time.api import API
from sandglass.time.filters import QueryFilter
from sandglass.time.models.project import Project
from sandglass.time.resource.model import ModelResource
from sandglass.time.schemas.project import ProjectListSchema
from sandglass.time.schemas.project import ProjectSchema


class ByUserOrPublic(QueryFilter):
    """
    Filter private projects that are now owned by current user.

    """
    def filter_query(self, query, request, resource):
        user = request.authenticated_user
        filters = or_(
            Project.user_id == user.id,
            Project.is_public == True,
        )
        return query.filter(filters)


class ProjectResource(ModelResource):
    """
    REST API resource for Project model.

    """
    name = 'projects'
    model = Project
    schema = ProjectSchema
    list_schema = ProjectListSchema

    @classmethod
    def get_query_filters(cls):
        filters = super(ProjectResource, cls).get_query_filters()
        return filters + (ByUserOrPublic(), )


API.register('v1', ProjectResource)
