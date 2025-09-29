Fine-Grained Authorization System
==================================

Trunk Player v0.1.5 introduces a comprehensive authorization system that allows fine-grained control over user access to radio systems, talkgroups, and system features.

Overview
--------

The authorization system is built around the concept of **multi-system access control**, where:

- Users can access multiple radio systems
- Each user has specific roles per system (Admin or Regular User)
- Access to talkgroups and features is controlled at the system level
- Personal preferences and scan lists are user-specific

Core Concepts
-------------

Systems
~~~~~~~

Radio systems represent individual radio networks (e.g., Police, Fire, EMS). Each system:

- Has its own set of talkgroups and units
- Maintains independent user access control
- Can have multiple administrators and users

User Roles
~~~~~~~~~~

There are two primary roles within each system:

**System Administrator**
  - Full access to all talkgroups in the system
  - Can manage other users' access to the system
  - Can edit talkgroup and unit names
  - Can assign specific talkgroup access to regular users

**Regular User**
  - Access only to specifically assigned talkgroups
  - Can manage personal menu preferences
  - Can create and manage personal scan lists
  - Cannot modify system data or manage other users

System Permissions
~~~~~~~~~~~~~~~~~~

Fine-grained permissions control specific capabilities:

- ``edit_talkgroups``: Edit talkgroup names and properties
- ``edit_units``: Edit unit names and descriptions
- ``manage_users``: Manage system user access and roles
- ``view_all_transmissions``: Access all transmissions in system
- ``download_audio``: Download audio files

User Management
---------------

Creating System Administrators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Access Django Admin interface
2. Navigate to **Radio > System roles**
3. Click **Add system role**
4. Select user, system, and set role to "System Administrator"
5. Save - the user now has full access to that system

Assigning Talkgroup Access
~~~~~~~~~~~~~~~~~~~~~~~~~~

System administrators can grant talkgroup access to regular users:

1. In Django Admin, go to **Radio > User talkgroup access**
2. Click **Add user talkgroup access**
3. Select the target user and talkgroup
4. Save to grant access

Alternatively, use the inline editor when viewing a System Role to manage multiple talkgroup assignments.

Personal Features
-----------------

Menu Customization
~~~~~~~~~~~~~~~~~~

Users can customize which talkgroups appear in their personal menu:

1. Visit ``/manage/menu/`` for bulk management
2. Use ``/talkgroups/manage/`` for individual toggles
3. Set display order for menu items
4. Changes are saved automatically

Custom Scan Lists
~~~~~~~~~~~~~~~~~

Users can create personal scan lists from their accessible talkgroups:

1. Navigate to ``/manage/scan-lists/``
2. Click **Create New Scan List**
3. Name the scan list and optionally add description
4. Select talkgroups from accessible systems
5. Mark as default if desired

Scan lists can be:

- **Active/Inactive**: Control visibility in menus
- **Default**: Automatically selected for scanning
- **Named**: Descriptive names for easy identification

API Changes
-----------

All API endpoints now require authentication and filter data based on user permissions:

Secure Endpoints
~~~~~~~~~~~~~~~~

- ``/api_v1/transmission/`` - Only transmissions from accessible talkgroups
- ``/api_v1/talkgroups/`` - Only talkgroups user has access to
- ``/api_v1/menutalkgrouplist/`` - User's personal menu talkgroups
- ``/api_v1/menuscanlist/`` - User's personal scan lists

Authentication Required
~~~~~~~~~~~~~~~~~~~~~~~

Anonymous access is controlled by the ``ALLOW_ANONYMOUS`` setting. When disabled:

- All data access requires user authentication
- Users only see data they have permission to access
- API responses are filtered by user's system roles

Slug System
-----------

Unique Identification
~~~~~~~~~~~~~~~~~~~~~

To prevent conflicts across systems, all slugs now include prefixes:

- **TalkGroup slugs**: ``sys{system_id}-{alpha_tag}`` (e.g., ``sys1-police-dispatch``)
- **UserScanList slugs**: ``user{user_id}-{name}`` (e.g., ``user5-emergency-services``)

This ensures:

- Global uniqueness across all systems
- Clear identification of ownership/system
- Reliable URL routing without conflicts

Migration Guide
---------------

Upgrading from Previous Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The authorization system is automatically installed via Django migrations:

1. **Backup your database** before upgrading
2. Run migrations: ``python manage.py migrate radio``
3. Create system administrators via Django admin
4. Assign users to systems as needed
5. Configure talkgroup access for regular users

Existing data is preserved, but users will need to be explicitly assigned to systems to maintain access.

Configuration
~~~~~~~~~~~~~

Key settings for the authorization system:

.. code-block:: python

    # Require authentication for all data access
    ALLOW_ANONYMOUS = False

    # Enable fine-grained access control
    ACCESS_TG_RESTRICT = True

Best Practices
--------------

System Organization
~~~~~~~~~~~~~~~~~~~

- Create separate systems for different agencies/departments
- Assign dedicated system administrators for each system
- Use descriptive system names and IDs
- Regular review of user access and permissions

User Management
~~~~~~~~~~~~~~~

- Grant minimum necessary access to regular users
- Use scan lists to organize talkgroups by function
- Encourage users to customize their menus for efficiency
- Regular audit of system administrators and their permissions

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

- System administrators have significant power - choose carefully
- Regular users should only have access to necessary talkgroups
- Monitor system access logs for unauthorized attempts
- Keep Django admin access restricted to trusted staff

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Users can't see any talkgroups**
  Check that the user has been assigned to at least one system with a role.

**System admin can't manage users**
  Verify the user has the 'manage_users' permission for that system.

**Scan lists not appearing in menu**
  Ensure scan lists are marked as Active and contain accessible talkgroups.

**API returning empty results**
  Confirm user authentication and system role assignments.

For additional support, consult the main documentation or community forums.