============
Upgrade to Trunk Player 0.1.2
============
This document will show you how to upgrade trunk Player 0.0.1 to 0.1.2

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



Remove Old Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove old env direactor to allow of clean package upgrades

.. code-block:: console

    $ rm -rf env/


Setup Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~

Setup a new Python 3.x virtual environment in the ``env`` direcory. Set the visual prompt to ``(Trunk Player)``.

.. code-block:: console

    $ virtualenv -p python3 env --prompt='(Trunk Player)'


Activate Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to re run this step each time you start a new shell or log into your machine.

.. code-block:: console

  $ source env/bin/activate

This will set you into a new python environment any packages you install via ``pip`` will only live in this area and do not touch your system files. This allowed you to have multiple projects with different dependencies. 


You can use the command ``deactivate`` to exit back to your normal system environment.

Re-Install Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~

First Upgrade pip

.. code-block:: console

  (Trunk Player)$ pip install --upgrade pip

Using pip install all required packages from the ``requirements.txt`` file.

.. code-block:: console

  (Trunk Player)$ pip install -r requirements.txt


Backup Postgres Database
~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a postgres database backup incase you have migration issues

Log into your postgres database as an admin user and dump the database, assuiming database name ``trunk_player``

.. code-block:: console

  $ sudo su - postgres
  (postgres)$ pg_dump trunk_player > /tmp/tunk_player.bak.sql
  (postgres)$ chmod 744 /tmp/tunk_player.bak.sql
  (postgres)$ exit
  $ cp /tmp/trunk_player.bak.sql ~/


Your backup is at ``/home/radio/tunk_player.bak.sql``

Upgrade the database
~~~~~~~~~~~~~~~~~~~~~~~

Using the `django manage.py`_ command to upgrade the database.

.. _django manage.py: https://docs.djangoproject.com/en/dev/ref/django-admin/


.. code-block:: console

  (Trunk Player)$ ./manage.py migrate


Starting the test web server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First note this is not full producation ready server. It can handle a couple users.

Using the ``manage.py`` command agian

.. code-block:: console

  
  (Trunk Player)$ ./manage.py check
  (Trunk Player)$ ./manage.py runserver

This will start the server up listening on the local loopback address on port ``8000``. Start your web browser and go to `http://localhost:8000`_. You should seen the main page
Visit ``/admin/`` to log into the admin area.

.. _`http://localhost:8000`: http://localhost:8000

If you are running this on a remote server you need to have the web server us its' public IP adress so you can connect.

.. code-block:: console

   (Trunk Player)$ ./manage.py runserver 0.0.0.0:8000

This will run the server also on port 8000 but will be accessible via the servers IP address or dns name on port ``8000`` also.

Restarting Trunk Player
~~~~~~~~~~~~~~~~~~~~~~~

If using supervisor do the following

.. code-block:: console

  $ sudo supervisorctl start trunkplayer:

You Did It!
===========

You have upgraded trunk player to 0.1.2! If you run into any issues open an issue at https://github.com/ScanOC/trunk-player/issues


Rollback Trunk-Player Install
=============================

Rollback Trunk-Player Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reset to Trunk-Player 0.0.1

.. code-block:: console

  (Trunk Player)$ git reset --hard cb22634f43a4e8ca233847a4d0e2864b3f7d1f2b

Rollback Postgres Database (Only if needing to rollback)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Log into your postgres database as an admin user and restore the database, assuiming database name ``trunk_player``

.. code-block:: console

  $ chmod 744 /home/radio/tunk_player.bak.sql
  $ sudo su - postgres
  (postgres)$ psql

Drop the Database; and recreate 

.. code-block:: console

  postgres=# DROP DATABASE trunk_player;
  postgres=# CREATE DATABASE trunk_player;
  postgres=#\q;

Restore Database

.. code-block:: console

  (postgres)$ psql trunk_player < /home/radio/tunk_player.bak.sql
  (postgres)$ exit

Remove Old Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove old env direactor to allow of clean package upgrades

.. code-block:: console

    $ rm -rf env/


Setup Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~

Setup a new Python 3.x virtual environment in the ``env`` direcory. Set the visual prompt to ``(Trunk Player)``.

.. code-block:: console

    $ virtualenv -p python3 env --prompt='(Trunk Player)'


Activate Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to re run this step each time you start a new shell or log into your machine.

.. code-block:: console

  $ source env/bin/activate

This will set you into a new python environment any packages you install via ``pip`` will only live in this area and do not touch your system files. This allowed you to have multiple projects with different dependencies. 


You can use the command ``deactivate`` to exit back to your normal system environment.

Re-Install Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~

First Upgrade pip

.. code-block:: console

  (Trunk Player)$ pip install --upgrade pip

Using pip install all required packages from the ``requirements.txt`` file.

.. code-block:: console

  (Trunk Player)$ pip install -r requirements.txt

Restarting Trunk Player
~~~~~~~~~~~~~~~~~~~~~~~

If using supervisor do the following

.. code-block:: console

  $ sudo supervisorctl start trunkplayer:
