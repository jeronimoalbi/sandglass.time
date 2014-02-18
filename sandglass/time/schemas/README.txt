API CALLS WITH CURL:
====================

/users/

curl -X POST -H "Content-Type: application/json" -d '{"users": [ {"email": "foo@example.com", "first_name": "max", "last_name": "angerbauer"} ] }' http://0.0.0.0:6543/time/api/v1/users/
curl -X PUT -H "Content-Type: application/json" -d '{"email": "foo@example.com", "first_name": "max", "last_name": "angerbauer"}' http://0.0.0.0:6543/time/api/v1/users/1/
curl -X DELETE http://0.0.0.0:6543/time/api/v1/users/1/