import pytest


@pytest.mark.usefixtures('default_data')
def test_auth_basic(request_helper):
    # Default user key should work for API requests
    response = request_helper.get_json('/time/api/v1/users/')
    assert response.status == '200 OK'

    # Use an invalid user key to make a request.
    # When request is not an Ajax request, HTTP 401 is
    # used to challenge the browser to authenticate.
    request_helper.auth_key = 'INVALID KEY'
    response = request_helper.get_json('/time/api/v1/users/')
    assert response.status == '401 Unauthorized'

    # Use an invalid user key to make an Ajax request.
    # In this case HTTP 403 is used because no auth challenge is required.
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    response = request_helper.get_json('/time/api/v1/users/', headers=headers)
    assert response.status == '403 Forbidden'
