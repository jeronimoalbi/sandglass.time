SQL/Models
==========

 * Add migration support. See: http://code.google.com/p/sqlalchemy-migrate/
   or http://alembic.readthedocs.org/en/latest/.
 * Add tablename prefix with the name of the sandglass module where the model
   is defined (like django).


 Tests
 =====

  * Implement base test case class(es) in ``test/__init__.py``.
  * Make coverage work.
  * Add tox support to enable tests for py27, py3.2 and py3.3.
  * Remove test requirements from setup.py (See: setuptools's tests_require)
