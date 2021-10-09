============
Upgrade to Trunk Player 0.1.3
============

**MAKE SURE  YOU ARE RUNNING 0.1.2** If you are not it will break Trunk Player

This document will show you how to upgrade trunk Player 0.1.2 to 0.1.3

**NEW USERS DO NOT NEED TO DO THIS**

Currently install is based on a Debian like system, Ubuntu.

System Prerequisites
====================

* Linux Machine with current Trunk Player install
* `Python`_ >=3.8.x
* `Virtualenv`_
* `PIP`_  Should be installed with Python 3
* `Redis`_ >=5.x.x 
* `PostgreSQL`_ 9.x
* `git`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _redis: http://redis.io/
.. _PIP: https://pypi.python.org/pypi/pip
.. _PostgreSQL: https://www.postgresql.org/
.. _git: https://git-scm.com/


Upgrade your system

.. code-block:: console

    $ sudo apt update && sudo apt upgrade




Assumptions
===========

* Project directory is ``/home/radio/trunk-player`` - You can replace ``/home/radio`` with your own home directory.
* Redis is running and listening on default port of ``:6379``

Upgrading Trunk Player
====================

The source is on GitHub, use git to upgrade your repo. Starting from your home directory of ``/home/radio/trunk-player``

.. code-block:: console

  $ cd /home/radio/trunk-player && git pull

This will pull down the most current version of Trunk Player.


Stopping Trunk Player
~~~~~~~~~~~~~~~~~~~~

We need to fre the database to upgrade so stop trunk player. **BE SURE TO STOP TRUNK PLAYER**

If using supervisor do the following

.. code-block:: console

  $ sudo supervisorctl stop trunkplayer:



Restarting Trunk Player
~~~~~~~~~~~~~~~~~~~~~~~

If using supervisor do the following

.. code-block:: console

  $ sudo supervisorctl start trunkplayer:

You Did It!
===========

You have upgraded trunk player to 0.1.3! If you run into any issues open an issue at https://github.com/ScanOC/trunk-player/issues
