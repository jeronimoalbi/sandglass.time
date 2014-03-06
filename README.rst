.. image:: https://drone.io/bitbucket.org/sandglass/sandglass.time/status.png
   :alt: Continuous Integration Service
   :target: https://drone.io/bitbucket.org/sandglass/sandglass.time/latest

Sandglass Time Documentation
============================

Time tracking application.

Setting up after initial checkout
---------------------------------

.. code:: bash

  $ python setyp.py develop
  $ cp sandglass-tests.ini.dist sandglass-tests.ini
  $ cp sandglass.ini.dist sandglass.ini
  $ sandglass manage init-database
  $ sandglass manage create-user --admin
  $ pserve sandglass.ini

