Upgrade to Version 0.1.5
========================

Version 0.1.5 introduces significant changes to the authorization system and data access patterns. This guide will help you upgrade safely while preserving your existing data.

⚠️ Important Notes
------------------

**This is a major update** that changes how user access is managed. Please read this guide completely before upgrading.

**Backup Required**: Always backup your database before performing this upgrade.

**User Access Changes**: After upgrade, users will need to be explicitly assigned to systems to maintain access to talkgroups.

What's Changed
--------------

Authorization System
~~~~~~~~~~~~~~~~~~~~

- **New Models**: SystemRole, SystemPermission, UserTalkgroupAccess, UserTalkgroupMenu, UserScanList
- **API Security**: All endpoints now require authentication and filter by user permissions
- **Multi-System Support**: Users can have different roles across multiple radio systems
- **Personal Features**: User-customizable menus and scan lists

Database Schema
~~~~~~~~~~~~~~~

- **New Tables**: Fine-grained authorization tables added
- **Slug Changes**: TalkGroup and UserScanList slugs now use unique prefixes
- **Enhanced Indexes**: Improved performance for permission queries

Upgrade Process
---------------

Step 1: Backup Database
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # PostgreSQL example
    pg_dump your_database_name > backup_pre_0.1.5.sql

    # SQLite example
    cp db.sqlite3 db_backup_pre_0.1.5.sqlite3

Step 2: Stop Application
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Docker
    docker compose down

    # Traditional install
    systemctl stop trunk-player

Step 3: Update Code
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git pull origin master
    # or download new release

Step 4: Update Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Docker - rebuild containers
    docker compose build

    # Traditional install
    pip install -r requirements.txt

Step 5: Run Migrations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Docker
    docker compose run --rm app python manage.py migrate radio

    # Traditional install
    python manage.py migrate radio

The migration will:

- Create new authorization tables
- Update existing slug fields with system prefixes
- Preserve all existing talkgroup and transmission data

Step 6: Configure System Access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After migration, configure user access:

1. **Access Django Admin**: ``/admin/``

2. **Create System Administrators**:

   - Go to **Radio > System roles**
   - Click **Add system role**
   - Select user, system, and role "System Administrator"
   - Save

3. **Assign Regular Users**:

   - Add system roles for regular users
   - Use **Radio > User talkgroup access** to assign specific talkgroups

Step 7: Test and Verify
~~~~~~~~~~~~~~~~~~~~~~~

1. **Test User Login**: Ensure users can log in and see appropriate talkgroups
2. **Verify API Access**: Check that ``/api_v1/talkgroups/`` returns filtered results
3. **Test Scan Lists**: Create and test user scan lists
4. **Check Menu Customization**: Verify menu preference functionality

Step 8: Start Application
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Docker
    docker compose up -d

    # Traditional install
    systemctl start trunk-player

Post-Upgrade Configuration
--------------------------

Recommended Settings
~~~~~~~~~~~~~~~~~~~~

Update your settings for enhanced security:

.. code-block:: python

    # Disable anonymous access
    ALLOW_ANONYMOUS = False

    # Enable access restrictions
    ACCESS_TG_RESTRICT = True

User Training
~~~~~~~~~~~~~

Inform your users about new features:

- **Menu Customization**: Users can now customize their talkgroup menus at ``/manage/menu/``
- **Scan Lists**: Personal scan lists can be created at ``/manage/scan-lists/``
- **System View**: Users can see their system access at ``/user/systems/``

Administrator Tasks
~~~~~~~~~~~~~~~~~~~

System administrators should:

1. **Review User Access**: Audit who has access to which systems
2. **Configure Permissions**: Set appropriate permissions for system roles
3. **Test Functionality**: Verify all features work as expected
4. **Document Changes**: Update any local documentation or procedures

Troubleshooting
---------------

Migration Issues
~~~~~~~~~~~~~~~~

**"relation already exists" errors**
  This can happen if migrations are run multiple times. The migrations are designed to handle this gracefully.

**Slug conflicts**
  The migration updates slugs with system prefixes to prevent conflicts. No manual intervention needed.

Access Issues
~~~~~~~~~~~~~

**Users can't see talkgroups after upgrade**
  Users need to be assigned to systems via Django admin. No access is granted automatically.

**API returns empty results**
  Ensure users have proper system roles assigned and are authenticated.

**Scan lists not working**
  Check that scan lists contain talkgroups the user has access to.

Performance
~~~~~~~~~~~

**Slow page loads**
  The new authorization system adds permission checks. Consider:

  - Database indexing (automatic with migrations)
  - Caching configuration
  - Review of large talkgroup lists

Rollback Procedure
------------------

If issues arise, you can rollback:

.. warning::
   Rollback will lose any new authorization data created after upgrade.

1. **Stop application**
2. **Restore database backup**
3. **Revert code to previous version**
4. **Restart application**

Migration Details
-----------------

The upgrade includes these migrations:

**0063_add_fine_grained_auth.py**
  - Creates all new authorization models
  - Adds indexes for performance
  - Sets up proper foreign key relationships

**0064_update_slugs_for_uniqueness.py**
  - Adds slug field to UserScanList
  - Updates existing TalkGroup slugs with system prefixes
  - Generates initial slugs for scan lists

**0065_make_slugs_unique.py**
  - Adds unique constraints to slug fields
  - Ensures data integrity

Support
-------

If you encounter issues during upgrade:

1. **Check logs**: Review Django and database logs for errors
2. **Community**: Post in the Trunk Player Google Group
3. **GitHub**: Open an issue with specific error details
4. **Documentation**: Review the authorization documentation

Remember to include:

- Your previous Trunk Player version
- Database backend (PostgreSQL, SQLite, etc.)
- Specific error messages
- Steps that led to the issue