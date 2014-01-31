SQL/Models
==========

 * Add migration support. See: http://code.google.com/p/sqlalchemy-migrate/
   or http://alembic.readthedocs.org/en/latest/.
 * Add support to override any model definition.

Tests
=====

  * Add tox support to enable tests for py27, py3.2 and py3.3.
  * Remove test requirements from setup.py (See: setuptools's tests_require)

API
===

 * Define error codes for reponses
 * Implement support to get partial data from related items (x.e ?include=tags:full)
 * Implement a Sphinx extension to auto document api resources
