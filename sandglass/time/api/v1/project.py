from sqlalchemy import or_

from sandglass.time.api.model import ModelResource
from sandglass.time.filters import QueryFilter
from sandglass.time.schemas.project import ProjectListSchema
from sandglass.time.schemas.project import ProjectSchema
from sandglass.time.models.project import Project


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
    query_filters = (
        ByUserOrPublic(),
    )
