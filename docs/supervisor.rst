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

Also, Edit the ``user=radio`` entries in ``trunk_player/supervisor.conf`` to match your desired user.  Keep in mind this user must have read/write permissions to your installation directory.

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
