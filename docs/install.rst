============
Installation
============
This document will show you how to get up and running with Trunk Player.

Currently install is based on a Debian like system, Ubuntu.

System Prerequisites
====================

* Linux Machine it might work in windows but has not been tested
* `Python`_ 3.5.x
* `Virtualenv`_
* `PIP`_  Should be installed with Python 3
* `Redis`_ 3.x.x 
* `PostgreSQL`_ 9.x
* `git`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _redis: http://redis.io/
.. _PIP: https://pypi.python.org/pypi/pip
.. _PostgreSQL: https://www.postgresql.org/
.. _git: https://git-scm.com/


Using apt-get

.. code-block:: console

    $ sudo apt-get install python3-dev virtualenv redis-server python3-pip postgresql libpq-dev postgresql-client postgresql-client-common git


Assumptions
===========

* Project directory is ``/home/radio/trunk-player`` - You can replace ``/home/radio`` with your own home directory.
* Redis is running and listening on default port of ``:6379``

Getting Trunk Player
====================

The source is on GitHub, use git to clone the repository. Starting from your home directory of ``/home/radio``

.. code-block:: console

  $ git clone https://github.com/ScanOC/trunk-player.git

This will pull down the most current version of Trunk Player.

Setup Virtual Environment
=========================

Setup a new Python 3.x virtual environment in the ``env`` direcory. Set the visual prompt to ``(Trunk Player)``.

.. code-block:: console

    $ cd trunk-player
    $ virtualenv -p python3 env --prompt='(Trunk Player)'

Activate Virtual Environment
============================

You will need to re run this step each time you start a new shell or log into your machine.

.. code-block:: console

  $ source env/bin/activate

This will set you into a new python environment any packages you install via ``pip`` will only live in this area and do not touch your system files. This allowed you to have multiple projects with different dependencies. 


You can use the command ``deactivate`` to exit back to your normal system environment.

Install Python Packages
=======================

Using pip install all required packages from the ``requirements.txt`` file.

.. code-block:: console

  (Trunk Player)$ pip install -r requirements.txt

Configure for first use
=======================

You will need to setup a local version of the setting.py file, create and initialize the database, and create a default admin account.

Local settings file
~~~~~~~~~~~~~~~~~~~
You will need to create a local settings file to override any settings in the ``trunk_player/settings.py`` file. This will allow you to pull down updates from GitHub without losing your local settings.

Make a copy of the sample local settings file

.. code-block:: console

  (Trunk Player)$ cp trunk_player/settings_local.py.sample trunk_player/settings_local.py

**Important** You need to set/change the ``SECRET_KEY`` in the ``trunk_player/settings_local.py``. This value is used to protect sensitive data like passwords. If you keep the one from the project a bad actor may be able to compromise your site or worse your server. See the django project about `SECRET_KEY`_.

.. _SECRET_KEY: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY

Configure Postgres Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a postgres user that has full access to your database.

Logged into your postgres database as an admin user

.. code-block:: console

  $ sudo su - postgres
  (postgres)$ psql

Create your user (trunk_player_user, with pass CHANGE_ME)

.. code-block:: console

  postgres=# CREATE USER trunk_player_user WITH PASSWORD 'CHANGE_ME';

Create your database named trunk_player

.. code-block:: console

  postgres=# CREATE DATABASE trunk_player;

Allow your user full control of the new DB

.. code-block:: console

  postgres=# GRANT ALL PRIVILEGES ON DATABASE trunk_player TO trunk_player_user;

Configure some settings as recomended by `Django`_

.. code-block:: console

  ALTER ROLE trunk_player_user SET client_encoding TO 'utf8';
  ALTER ROLE trunk_player_user SET default_transaction_isolation TO 'read committed';
  ALTER ROLE trunk_player_user SET timezone TO 'UTC';

.. _Django: https://docs.djangoproject.com/en/1.11/ref/databases/#postgresql-notes


Exit from postgres and back to your user

.. code-block:: console

  postgres=# \q
  (postgres)$ exit
  $


Edit the ``trunk_player/settings_local.py`` and configure the DATABASES to match your server/username/passwords.


Initialize the database
~~~~~~~~~~~~~~~~~~~~~~~

Using the `django manage.py`_ command to build the new database.

.. _django manage.py: https://docs.djangoproject.com/en/dev/ref/django-admin/


.. code-block:: console

  (Trunk Player)$ ./manage.py migrate

Create admin account
~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

  (Trunk Player)$ ./manage.py createsuperuser
  Username: test
  Email address: test@sample.com
  Password: mypassword
  Password (again): mypassword
  Superuser created successfully.


Starting the test web server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First note this is not full producation ready server. It can handle a couple users.

Using the ``manage.py`` command agian

.. code-block:: console

  (Trunk Player)$ ./manage.py runserver

This will start the server up listening on the local loopback address on port ``8000``. Start your web browser and go to `http://localhost:8000`_. You should seen the main page
Visit ``/admin/`` to log into the admin area.

.. _`http://localhost:8000`: http://localhost:8000

If you are running this on a remote server you need to have the web server us its' public IP adress so you can connect.

.. code-block:: console

   (Trunk Player)$ ./manage.py runserver 0.0.0.0:8000

This will run the server also on port 8000 but will be accessible via the servers IP address or dns name on port ``8000`` also.
