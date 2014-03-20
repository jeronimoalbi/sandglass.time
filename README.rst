.. image:: https://drone.io/bitbucket.org/sandglass/sandglass.time/status.png
   :alt: Continuous Integration Service
   :target: https://drone.io/bitbucket.org/sandglass/sandglass.time/latest

=======================
Sandglass Documentation
=======================

Sandglass is a REST API based time tracking application.

It relies on the `Pyramid`_ web framework and `SQLAlchemy`_ for data access.

.. _Pyramid: http://www.pylonsproject.org/
.. _SQLAlchemy: http://www.sqlalchemy.org/

Setting up after initial checkout
---------------------------------

.. code:: bash

  $ python setyp.py develop
  $ cp sandglass-tests.ini.dist sandglass-tests.ini
  $ cp sandglass.ini.dist sandglass.ini
  $ sandglass manage init-database
  $ sandglass manage create-user --admin
  $ pserve sandglass.ini

********
Frontend
********

Frontend implementation is being developed as a separate project called `sandglass-frontend`_.

.. _sandglass-frontend: https://github.com/gustavpursche/sandglass-frontend
