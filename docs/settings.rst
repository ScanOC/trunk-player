================================
Settings - List of all settings
================================

This document will list all settings used by trunk player. The settings are read from the base settings file ``trunk_player/settings.py`` and also the local file you can override ``trunk_player/settings_local.py``

These include settings from the base Django code. `Complete list from Django`_ These will be prefixed with a [D], Settings for 3rd party django apps will be prefixed with [D3]


.. _Complete list from Django: https://docs.djangoproject.com/en/1.11/topics/settings/


SITE_TITLE
==========

This value will be used for html page titles.

SECRET_KEY
==========

[D] Django secret key. Used by the system for all encoding and encrypting of values. **Very important you change this to your own random value**

DEBUG
=====

[D] When DEUG is True Djago will display debug messages for error on the web page. You do not want this set on an open site. This can expose sensitive data to users.

ALLOWED_HOSTS
=============

[D] This is a list of host names the web page can be accessed in, you need to set this domain name(s) of your site.

DATABASES
=========

[D] Configuration data for your database connection

SITE_EMAIL
==========

Email address emails will come from

DEFAULT_FROM_EMAIL
==================

Email address emails will come from

AUDIO_URL_BASE
==============

URL where your audio files are accessiable at

ANONYMOUS_TIME
==============

Time in minutes that an anonymous (non logged in) can view into the past

TIME_ZONE
=========

[D] Timezone settings

`List of timezones`_ You can set to your local timezone.

.. _List of timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

ACCESS_TG_RESTRICT
==================

If set to true all talkgroups are restricted and each user needs to be explicitly granted permission in the talkgroupaccess table

GOOGLE_ANALYTICS_PROPERTY_ID
============================

Google ID used for analytics

TWITTER_ACTIVE
==============

If set to true it will display a twitter feed to the right
``TWITTER_LIST_URL`` the url for the feed

LOGIN_REDIRECT_URL
==================

[D3] Where the user is redirected after they login


.. note:: The settings below this point will most likely not need to be edited

JS_SETTINGS
===========

Used to allow the page javascript visibility into the settings in the list

JS_SETTINGS
===========

Used to allow the django HTML template engine visibility into the settings in the list

ALLOW_ANONYMOUS
===============

**Default:** ``False`` (as of v0.1.5)

Controls whether anonymous (unauthenticated) users can access any data. When set to ``False``, all API endpoints and data access requires user authentication. When ``True``, public talkgroups and transmissions may be accessible to anonymous users.

**Security Note:** Setting this to ``False`` is recommended for production environments with sensitive radio traffic.


RADIO_DEFAULT_UNIT_AGENCY
=========================

DB ID of the default acency when a new unit is added
* This is defaulted to 0 which is invalid in mysql

AMAZON_ADDS
===========

If set to true the site will display amazons ads on the right hand side

Additinal settings for this are :
``AMAZON_AD_TRACKING_ID`` Your Amazon ID
``AMAZON_AD_LINK_ID`` ID for this site
``AMAZON_AD_EMPHASIZE_CATEGORIES`` Categories to display
``AMAZON_AD_FALL_BACK_SEARCH`` Search terms

SOCIALACCOUNT_PROVIDERS
=======================

[D3] Config settings to allow google authentication

ACCOUNT_AUTHENTICATION_METHOD
=============================

[D3] Default username setup

ACCOUNT_EMAIL_REQUIRED
======================

[D3] Require email address

BASE_DIR
========

[D] Base directory the project is installed in.

LOGIN_URL
=========

[D] The url django will redirect users who are not looged in when a page requires login.

INSTALLED_APPS
==============

[D] List of the django apps that make up the project.

MIDDLEWARE_CLASSES
==================

[D] List of middleware code that is run in the project

ROOT_URLCONF
============

[D] Where the primary URL list comes from

TEMPLATES
=========

[D] Config values for the HTML template system

WSGI_APPLICATION
================

[D] Location of the config file for the primary web setup

AUTHENTICATION_BACKENDS
=======================

[D] How users are authenticated to django

AUTH_PASSWORD_VALIDATORS
========================

[D] How password are validated

LANGUAGE_CODE
=============

[D] Language used

USE_I18N
========

[D] Use Language code

USE_L10N
========

[D] localized formatting

USE_TZ
======

[D] Use localtime zones

SECURE_PROXY_SSL_HEADER
=======================

[D] Used to make sure HTTPS connections are set

STATIC_URL
==========

[D] URL Prefix for static content

STATIC_ROOT
===========

[D] Directory location of static files

REST_FRAMEWORK
==============

[D] Config for the REST (API) framework

MEDIA_URL
=========

[D] URL prefix for media data

MEDIA_URL
=========

[D] Directory location of media files

CHANNEL_LAYERS
==============

[D] Config of the channel app. This is where the websock data is accessed from.

CACHES
======

[D] Config of the local cache

SITE_ID
=======

[D] ID of this site

USE_RAW_ID_FIELDS
=================

[D] For very large systems, the admin page may load better with raw id fields


Authorization System Settings (v0.1.5+)
========================================

The following settings control the fine-grained authorization system introduced in version 0.1.5.

ACCESS_TG_RESTRICT
==================

**Default:** ``True`` (as of v0.1.5)

When enabled, enforces fine-grained talkgroup access control. Users will only see talkgroups they have been explicitly granted access to through the SystemRole and UserTalkgroupAccess models.

When disabled, falls back to the legacy TalkGroupAccess system for backward compatibility.

**Recommended:** ``True`` for new installations using the fine-grained authorization system.

REQUIRE_SYSTEM_ROLE
===================

**Default:** ``True`` (as of v0.1.5)

When enabled, users must have at least one SystemRole assignment to access any talkgroup data. This ensures all access is explicitly controlled through the authorization system.

**Security Note:** Keep enabled to prevent unauthorized data access.

DEFAULT_SYSTEM_ADMIN_PERMISSIONS
=================================

**Default:** ``['edit_talkgroups', 'edit_units', 'manage_users', 'view_all_transmissions']``

List of permissions automatically granted to System Administrators. These permissions are automatically applied when a user is assigned the "System Administrator" role for any system.

Available permissions:

- ``edit_talkgroups``: Edit talkgroup names and properties
- ``edit_units``: Edit unit names and descriptions
- ``manage_users``: Manage system user access and roles
- ``view_all_transmissions``: Access all transmissions in system
- ``download_audio``: Download audio files

Example:

.. code-block:: python

    DEFAULT_SYSTEM_ADMIN_PERMISSIONS = [
        'edit_talkgroups',
        'edit_units',
        'manage_users',
        'view_all_transmissions',
        'download_audio'
    ]

ENFORCE_UNIQUE_SLUGS
====================

**Default:** ``True`` (as of v0.1.5)

Enforces unique slug generation with system/user prefixes. When enabled:

- TalkGroup slugs include system prefix: ``sys{system_id}-{alpha_tag}``
- UserScanList slugs include user prefix: ``user{user_id}-{name}``

This prevents slug conflicts across systems and users.

**Important:** Required for proper URL routing in multi-system environments.

MENU_TALKGROUP_LIMIT
====================

**Default:** ``50``

Maximum number of talkgroups a user can add to their personal menu. This prevents performance issues with very large personal menus.

Set to ``0`` for unlimited (not recommended for large systems).

SCAN_LIST_TALKGROUP_LIMIT
=========================

**Default:** ``100``

Maximum number of talkgroups allowed in a single user scan list. This prevents performance issues when processing large scan lists.

Set to ``0`` for unlimited (not recommended).

USER_SCAN_LIST_LIMIT
====================

**Default:** ``20``

Maximum number of scan lists a single user can create. This prevents database bloat from users creating excessive numbers of scan lists.

Set to ``0`` for unlimited.

AUTO_ASSIGN_NEW_TALKGROUPS
===========================

**Default:** ``False``

When enabled, newly created talkgroups are automatically assigned to all System Administrators in the same system. Regular users still require explicit assignment.

**Note:** This only affects System Administrators - regular users never receive automatic access.

LOG_PERMISSION_CHECKS
=====================

**Default:** ``False``

When enabled, logs all permission checks for debugging authorization issues. This can generate significant log volume and should only be enabled for troubleshooting.

**Warning:** Only enable in development or when debugging permission issues.

Example Configuration
=====================

Example settings for a production environment with fine-grained authorization:

.. code-block:: python

    # Security settings
    ALLOW_ANONYMOUS = False
    ACCESS_TG_RESTRICT = True
    REQUIRE_SYSTEM_ROLE = True
    ENFORCE_UNIQUE_SLUGS = True

    # Limits to prevent abuse
    MENU_TALKGROUP_LIMIT = 25
    SCAN_LIST_TALKGROUP_LIMIT = 50
    USER_SCAN_LIST_LIMIT = 10

    # Convenience features
    AUTO_ASSIGN_NEW_TALKGROUPS = True

    # Admin permissions
    DEFAULT_SYSTEM_ADMIN_PERMISSIONS = [
        'edit_talkgroups',
        'edit_units',
        'manage_users',
        'view_all_transmissions'
    ]

    # Debugging (disable in production)
    LOG_PERMISSION_CHECKS = False