Misc
====

 * Implement timezone support for dates (pytz)

SQL/Models
==========

 * Implement a better member 404 for ModelResources.
 * Add migration support. See: http://code.google.com/p/sqlalchemy-migrate/
   or http://alembic.readthedocs.org/en/latest/.

API
===

 * Define error codes for reponses
 * Implement support to get partial data from related items (x.e ?include=tags:full)
 * Define a standard way to use filters (from/to dates for example)
 * Implement support for returning JSON with camelcase field names
 * Add XML and JSONP formats support (use extension in URL ?)
 * Implement a Sphinx extension to auto document api resources

Tests
=====

 * Make python 3 work in tox. See:
   http://stackoverflow.com/questions/14892977/internationalization-with-pyramid-and-python-3
