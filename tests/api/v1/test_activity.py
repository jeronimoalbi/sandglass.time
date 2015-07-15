from sandglass.time.api.v1.activity import ActivityResource
from sandglass.time.api.v1.tag import TagResource
from sandglass.time.models.tag import TAG


def test_activity_add_and_delete_tags(request_helper, default_data, session):
    project = default_data.projects.public_project
    task = default_data.tasks.backend
    user = default_data.users.dr_who
    session.add_all([project, task, user])

    # Create a new activity
    activity_data = {
        'description': u"Test activity",
        'project_id': project.id,
        'task_id': task.id,
        'user_id': user.id,
    }
    url = ActivityResource.get_collection_path()
    response = request_helper.post_json(url, [activity_data])
    assert response.status == '200 OK'
    # All post to collection should returns a collection
    assert isinstance(response.json, list) is True
    # User updated information is returned a single item in a list
    response_data = response.json[0]
    activity_id = response_data['id']

    # Create some tags
    tags_data = [
        {'name': u"Tag 1", 'tag_type': TAG.activity.value, 'user_id': user.id},
        {'name': u"Tag 2", 'tag_type': TAG.activity.value, 'user_id': user.id},
    ]
    tags_url = TagResource.get_collection_path()
    response = request_helper.post_json(tags_url, tags_data)
    assert response.status == '200 OK'
    assert len(response.json) == len(tags_data)

    # Add tags to current activity
    tag_ids = [tag['id'] for tag in response.json]
    tag_ids.sort()
    url = ActivityResource.get_member_path(activity_id) + '@add-tags'
    response = request_helper.post_json(url, tag_ids)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == len(tag_ids)
    # Check that same tags were returned
    returned_tag_ids = [tag['id'] for tag in response.json]
    returned_tag_ids.sort()
    assert returned_tag_ids == tag_ids

    # Get tags using activity related path
    url = ActivityResource.get_related_path(activity_id, 'tags')
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == len(tag_ids)
    # Check that tags matches the added ones
    returned_tag_ids = [tag['id'] for tag in response.json]
    returned_tag_ids.sort()
    assert returned_tag_ids == tag_ids

    remove_tag_ids = list(returned_tag_ids)
    # Add a non existant ID to list (it should be completely ignored)
    remove_tag_ids.append(9999)
    # Remove first tag from activity
    url = ActivityResource.get_member_path(activity_id) + '@remove-tags'
    remove_tag_id = remove_tag_ids[0]
    response = request_helper.delete_json(url, [remove_tag_id])
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    # Check that only one tag ID was deleted
    assert len(response.json) == 1
    removed_tag = response.json[0]
    assert remove_tag_id == removed_tag['id']
    # Remove the last existing tag from activity.
    # From the 3 IDs ones was removed, the other does not exists
    # and only one still exists and is assigned to the activity.
    assert len(remove_tag_ids) == 3
    response = request_helper.delete_json(url, remove_tag_ids)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == 1
