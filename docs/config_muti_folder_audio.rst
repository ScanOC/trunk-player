==============================================
Configure - Local Audio Files Multiple Folders
==============================================
This document will show you how to configure Trunk Player using multiple folders to store and play back your audio in the same structure as trunk-recorder.

Currently install is based on a Debian like system, Ubuntu.

System Prerequisites
====================

* After configuring for Local Audio Files

* Trunk-player is in ``/home/radio/trunk-player``

* Audio files will be served via a web-server (nginx) from ``/home/radio/trunk-player/audio_files/``

* Trunk-recorder is in ``/home/radio/trunk-recorder``

* Both ``sox`` and ``lame`` installed.

Update trunk-player
===================

Change directory into the base trunk-player directory

.. code-block:: console

  $ cd /home/radio/trunk-player

Pull down latest version of trunk-player from github

.. code-block:: console

  $ git pull

Activate virtualenv

.. code-block:: console

  $ source env/bin/activate

Migrate any new database schema changes

.. code-block:: console

  $ ./manage.py migrate

Update Trunk-Recorder
=====================

Configure trunk-recorder to save our wav/json files in  ``/home/radio/trunk-player/audio_files/``

Edit the trunk-recorder config file ``/home/radio/trunk-recorder/config.json``

Change the ``captureDir`` to ``/home/radio/trunk-player/audio_files``

In the systems list for each system you have, edit the ``uploadScript`` to ``encode-local-sys-0.sh`` change the 0 to the system number you want it to be saved as in trunk-player

Save the config

Copy the sample script  ``/home/radio/trunk-player/utility/trunk-recoder/encode-local-sys-0.sh`` to ``/home/radio/trunk-recorder/``

.. code-block:: console

  $ cp utility/trunk-recoder/encode-local-sys-0.sh  /home/radio/trunk-recorder/encode-local-sys-0.sh

If you have multiple systems, update the zero ( 0 ) in the second part of the cp command for each system number

Running new config
==================

Re start both trunk-recorder and trunk-player.
