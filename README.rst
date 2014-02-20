Sandglass Time Documentation
============================

Time tracking application.

.. image:: https://drone.io/bitbucket.org/sandglass/sandglass.time/status.png
   :alt: Continuous Integration Service
   :target: https://drone.io/bitbucket.org/sandglass/sandglass.time/latest

Setting up after initial checkout
---------------------------------

$ python setyp.py develop
$ sandglass manage init-database
$ sandglass manage create-user --admin
$ pserve sandglass.ini