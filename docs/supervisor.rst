==========
Supervisor
==========
Using supervisor to run the web services


Install Supervisor
==================

.. code-block:: console

  $ sudo apt-get install supervisor


Update Config
=============

Copy ``trunk_player/supervisor.conf.sample`` to ``trunk_player/supervisor.conf``

Edit the ``/home/radio/trunk-player`` entries in ``trunk_player/supervisor.conf`` to match your install directory.

Enable the config
=================

First stop and disable any already running runserver, runworker or daphne processes.


Link in the config and refresh supervisor.

.. code-block:: console

  $ sudo ln -s /home/radio/trunk-player/trunk_player/supervisor.conf /etc/supervisor/conf.d/trunk_player.conf
  $ sudo supervisorctl reread
  $ sudo supervisorctl update


Restaring trunk-player
======================

If you make any code changes (git pull) you need to restart the web processes.

.. code-block:: console

  $ sudo supervisorctl restart trunkplayer:
