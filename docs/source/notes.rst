#######################
Sandglass Notes (DRAFT)
#######################

Last update: 21.03.2014

Sandglass is a REST API based application. It supports JSON/JSONP data formats.

API requests
============

The base entry point for Sandglass time API is /time/api/*VERSION*/, where *VERSION* is the API version to connect to.

Supported HTTP methods and resource URLs table:

  =================================================  ========================  ==========================  =====================================  ==========================================
  Resource URLs                                      POST                      GET                         PUT                                    DELETE
  =================================================  ========================  ==========================  =====================================  ==========================================
  /time/api/v1/*RESOURCE_NAME*/                      **Create** new object(s)  **List** member object(s)   **Update** member object(s)            **Delete** member object(s)
  /time/api/v1/*RESOURCE_NAME*/*ID*/                                           **Get** a member object     **Update** a member object             **Delete** a member object
  /time/api/v1/*RESOURCE_NAME*/*ID*/*RELATED_NAME*/                            **List** related object(s)  **Add** related object(s) to a member  **Remove** related object(s) from a member
  =================================================  ========================  ==========================  =====================================  ==========================================

By default all request and responses to *collections* only allow lists to be used in request body. Even for collection operations on a single object.
But is possible to disable this behavior and make API less restrictive.

API response for a GET request to `/time/api/v1/users/1/`:

.. code:: json

  {
    "first_name":"First User",
    "last_name":"Test",
    "created":"2014-03-03T14:28:53+00:00",
    "data":null,
    "modified":null,
    "id":1,
    "token":"f9ef6f9368873ccd0ac2a46e2b8874674d078a5e2fd9159a0b2855271fd2f425",
    "key":"7143b8d9d6dc4a33ec6972b343488a0634c0fe0ac3aa4960041bc73118cb5162",
    "email":"test.user@gmail.com"
  }


API response for a GET request to `/time/api/v1/users/`:

.. code:: json

    [
      {
        "first_name":"First User",
        "last_name":"Test",
        "created":"2014-03-03T14:28:53+00:00",
        "data":null,
        "modified":null,
        "id":1,
        "token":"f9ef6f9368873ccd0ac2a46e2b8874674d078a5e2fd9159a0b2855271fd2f425",
        "key":"7143b8d9d6dc4a33ec6972b343488a0634c0fe0ac3aa4960041bc73118cb5162",
        "email":"test.user@gmail.com"
      },
      {
        "first_name":"Second User",
        "last_name":"Test",
        "created":"2014-03-03T14:32:38+00:00",
        "data":null,
        "modified":"2014-03-04T18:28:08+00:00",
        "id":2,
        "token":"bd30bde701711d6c28e0b7e39f5f83374e2c96ff3664afb3a56d2253f790d516",
        "key":"5f45c45e717bd462b7d257fe9491dd68ecf106189d0e4dde333176d02e363267",
        "email":"test@example.com"
      }
    ]


Collection and Member Actions
=============================

API resource actions can be called for *collections* or for *members* by prefixing the `@` to an action name. For example, `/time/api/v1/users/@signin`.

Actions are used when business logic require more that inserting, updating, listing and deleting objects.

URL format for *collection* actions::

    /time/api/v1/RESOURCE_NAME/@ACTION_NAME

URL format for *member* actions::

    /time/api/v1/RESOURCE_NAME/ID/@ACTION_NAME

Related Query Modes
===================

Related query modes are used in GET requests to *collections* or *members* to also include related object data for each member.

By default no GET request include related object data.

There are 2 query modes, `pk` and `full`. The `pk` mode is used when none is specified.

Related object data is loaded using HTTP GET parameter `include` or `inc`. Its value is the name of the related field, and optionally the mode as prefix.

For example, a *member* request to get a user::

    /time/api/v1/users/1/?include=tags__full&inc=projects__pk&include=groups__full

And the response would look like:

.. code:: json

    {
      "first_name":"Test",
      "last_name":"User",
      "groups":[
        {
          "id":1,
          "name":"time.Administrators",
          "description":"Administrators"
        }
      ],
      "created":"2014-03-03T14:28:53+00:00",
      "data":null,
      "tags":[],
      "modified":null,
      "id":1,
      "token":"f9ef6f9368873ccd0ac2a46e2b8874674d078a5e2fd9159a0b2855271fd2f425",
      "key":"7143b8d9d6dc4a33ec6972b343488a0634c0fe0ac3aa4960041bc73118cb5162",
      "email":"test@example.com",
      "projects":[]
    }


Returned object fields
======================

The fields returned for each object can be specified using an HTTP GET argument `fields`. This is useful in case not all fields are needed to reduce request size.

The argument takes a comma separated list of field names.

For example, a *member* request to get a user with *email*, *token* and *key* fields::

    /time/api/v1/users/1/?fields=email,token,key

And the response would look like:

.. code:: json

    {
      "id":1,
      "token":"f9ef6f9368873ccd0ac2a46e2b8874674d078a5e2fd9159a0b2855271fd2f425",
      "key":"7143b8d9d6dc4a33ec6972b343488a0634c0fe0ac3aa4960041bc73118cb5162"
    }


API describe action
===================

Describe is a way of getting "live" information from the API.

It is implemented using an action called `@describe`. Action is applicable to root API version paths and also to collections.

A request to API v1 `/time/api/v1/@describe`:

.. code:: json

    {
      "version":"v1",
      "resources":[
        {
          "path":"/time/api/v1/activities/",
          "describe":"/time/api/v1/activities/@describe",
          "name":"activities",
          "doc":"REST API resource for Activity model."
        },
        {
          "path":"/time/api/v1/users/",
          "describe":"/time/api/v1/users/@describe",
          "name":"users",
          "doc":"REST API resource for User model."
        },
        ...

      ]
    }


A request to API v1 users collection `/time/api/v1/users/@describe`:

.. code:: json

    {
      "filters":[
        {
          "methods":["GET"],
          "doc":"Filter query results by some search field(s).\n\n    By default ...",
          "name":"search_fields",
          "fields":{
            "first_name":{
              "operations":["eq", "contains", "starts", "ends"],
              "type":"String"
            },
            "token":{
              "operations":["eq"],
              "type":"String"
            },
            "created":{
              "operations":["eq", "gt", "gte", "lt", "lte"],
              "type":"DateTime"
            }
          }
        }
      ],
      "related":["tags", "projects", "tasks", "groups"],
      "actions":{
        "member":[
          {
            "doc":"Get activities for current user.\n\n        By default ...",
            "request_method":"GET",
            "name":"activities",
            "permission":null
          }
        ],
        "collection":[
          {
            "doc":"Get an API resource description.",
            "request_method":"GET",
            "name":"describe",
            "permission":"time.api.describe"
          },
          {
            "doc":"Get a User by email or token.\n\n        Return a User or raise HTTP 404.",
            "request_method":"GET",
            "name":"search",
            "permission":null
          },
          {
            "doc":"Signin (login) a user.",
            "request_method":"POST",
            "name":"signin",
            "permission":"__no_permission_required__",
            "schema":{
              "password":{
                "doc":"",
                "type":"String"
              },
              "email":{
                "doc":"",
                "type":"String"
              },
              ...
            }
          },
          {
            "doc":"Create a new user.",
            "request_method":"POST",
            "name":"signup",
            "permission":"__no_permission_required__",
            "schema":{
              "first_name":{
                "doc":"",
                "type":"String"
              },
              "last_name":{
                "doc":"",
                "type":"String"
              },
              ...
            }
          }
        ]
      },
      "schema":{
        "first_name":{
          "doc":"",
          "type":"String"
        },
        "last_name":{
          "doc":"",
          "type":"String"
        },
        "id":{
          "doc":"",
          "type":"Integer"
        },
        ...
      }
    }


Authentication
==============

Currently only *Basic HTTP auth* is supported, but *oAuth 2* will also be supported for cases where better security is needed.

Basic HTTP auth authentication in the API uses a "token" and a "key" hash to authenticate user requests.
