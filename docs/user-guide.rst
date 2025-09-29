User Guide
==========

This guide covers the features available to regular users of Trunk Player. For administrative features, see the Authorization System documentation.

Getting Started
---------------

Account Access
~~~~~~~~~~~~~~

To use Trunk Player, you need:

1. **User Account**: Register or receive account credentials from your administrator
2. **System Access**: Your administrator must assign you to one or more radio systems
3. **Talkgroup Access**: You'll be granted access to specific talkgroups within each system

Once configured, you can access all features through the web interface.

Understanding Your Access
~~~~~~~~~~~~~~~~~~~~~~~~~~

Your access is organized by **Radio Systems**. Each system represents a different radio network (e.g., Police, Fire, EMS). You may have access to:

- **Multiple Systems**: Different radio networks with separate talkgroup sets
- **Different Roles**: You might be an admin in one system and regular user in another
- **Specific Talkgroups**: Within each system, you access only assigned talkgroups

View your system access at: **Your Systems** (``/user/systems/``)

Main Features
-------------

Viewing Transmissions
~~~~~~~~~~~~~~~~~~~~~

The main page shows recent radio transmissions from your accessible talkgroups:

- **Real-time Updates**: New transmissions appear automatically
- **Audio Playback**: Click play button to listen to recordings
- **Transmission Details**: View date, time, frequency, units involved
- **Emergency Alerts**: Emergency transmissions are highlighted

**Filtering Transmissions:**

- Use the search box to find specific transmissions
- Filter by talkgroup, unit, or date range
- Click talkgroup names to see only that talkgroup's traffic

Browsing Talkgroups
~~~~~~~~~~~~~~~~~~~

View all your accessible talkgroups at: **Talkgroups** (``/talkgroups/``)

The talkgroup list shows:

- **ID**: Talkgroup decimal ID
- **System**: Which radio system it belongs to
- **Alpha Tag**: Short identifier (e.g., "PD_DISPATCH")
- **Description**: Full description of the talkgroup's purpose

Click any alpha tag to view that talkgroup's recent transmissions.

Personal Customization
----------------------

Menu Preferences
~~~~~~~~~~~~~~~~

Customize which talkgroups appear in your personal menu for quick access.

**Quick Toggle** (``/talkgroups/manage/``):

- View all accessible talkgroups with menu status
- Click menu button to toggle talkgroup visibility
- Green rows indicate talkgroups in your menu
- Changes are saved automatically

**Bulk Management** (``/manage/menu/``):

- Select multiple talkgroups at once
- Set display order for menu items
- Use "Select All" buttons for entire systems
- Save changes when finished

**Tips:**

- Add frequently monitored talkgroups to your menu
- Set logical order numbers (10, 20, 30) for easy reordering
- Use system-specific groupings for organization

Custom Scan Lists
~~~~~~~~~~~~~~~~~

Create personal scan lists to monitor specific groups of talkgroups.

**Creating Scan Lists** (``/manage/scan-lists/``):

1. Click **Create New Scan List**
2. Enter a descriptive name (e.g., "Emergency Services")
3. Optionally add a description
4. Select talkgroups from your accessible systems
5. Mark as default if desired
6. Save your scan list

**Managing Scan Lists:**

- **Active/Inactive**: Control whether scan list appears in menus
- **Default**: Automatically selected when visiting scan pages
- **Edit**: Modify name, description, or talkgroup selection
- **Delete**: Remove scan lists you no longer need

**Using Scan Lists:**

- Click **Listen** button to hear transmissions from scan list talkgroups
- Access via scan URLs: ``/api_v1/scan/your-scan-list-name/``
- Scan lists appear in dropdown menus throughout the interface

Audio Features
--------------

Playback Controls
~~~~~~~~~~~~~~~~~

Each transmission includes audio controls:

- **Play/Pause**: Standard playback controls
- **Volume**: Adjust audio level
- **Speed**: Change playback speed (0.5x to 2x)
- **Download**: Save audio file (if permitted)

**Keyboard Shortcuts:**

- ``Space``: Play/pause current transmission
- ``Arrow Keys``: Skip between transmissions
- ``+/-``: Adjust volume

Emergency Transmissions
~~~~~~~~~~~~~~~~~~~~~~~

Emergency transmissions are highlighted with:

- **Red indicators**: Visual alert for emergency traffic
- **Priority placement**: Often appear at top of lists
- **Special notifications**: May include additional alerts

Quality and Technical Info
~~~~~~~~~~~~~~~~~~~~~~~~~~

Each transmission shows technical details:

- **Frequency**: Radio frequency used
- **Duration**: Length of transmission
- **Signal Quality**: Reception quality indicators
- **Source**: Recording source information

Navigation
----------

Main Menu
~~~~~~~~~

The top navigation provides access to:

- **Home**: Recent transmissions from all accessible talkgroups
- **Talkgroups**: Browse all accessible talkgroups
- **Your Menu**: Quick access to flagged talkgroups
- **Scan Lists**: Access to your custom scan lists
- **Profile/Settings**: Account and preference management

Quick Actions
~~~~~~~~~~~~~

Common actions available throughout the interface:

- **Talkgroup Links**: Click any talkgroup name for recent transmissions
- **System Filters**: Filter by specific radio system
- **Time Ranges**: View transmissions from specific time periods
- **Search**: Find transmissions by keywords or IDs

Mobile Experience
~~~~~~~~~~~~~~~~~

Trunk Player is mobile-friendly:

- **Responsive Design**: Adapts to phone and tablet screens
- **Touch Controls**: Optimized for touch interaction
- **Offline Capability**: Cache recent data for offline viewing
- **Quick Actions**: Swipe gestures for common tasks

Tips and Best Practices
-----------------------

Organization
~~~~~~~~~~~~

**Scan List Strategy:**

- Create topic-specific scan lists (e.g., "Emergency", "Routine", "Special Events")
- Use descriptive names you'll remember
- Set one default scan list for quick access
- Regularly review and update scan list contents

**Menu Organization:**

- Add only frequently used talkgroups to your menu
- Use logical ordering (emergency services first, etc.)
- Group related talkgroups with similar order numbers
- Periodically clean up unused menu items

Monitoring
~~~~~~~~~~

**Effective Monitoring:**

- Use scan lists to focus on relevant traffic
- Monitor emergency channels during active incidents
- Check multiple systems if you have access
- Set up notifications for high-priority talkgroups

**Audio Management:**

- Adjust volume for comfortable monitoring
- Use speed controls for faster review of recordings
- Download important recordings for offline reference
- Respect any download limitations set by administrators

Privacy and Etiquette
~~~~~~~~~~~~~~~~~~~~~

**Responsible Use:**

- Only access talkgroups you're authorized to monitor
- Respect sensitive information in transmissions
- Don't share audio recordings without permission
- Follow any organizational policies about radio monitoring

**Account Security:**

- Keep your login credentials secure
- Log out when using shared computers
- Report any unauthorized access to administrators
- Review your system access periodically

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Can't see any talkgroups:**

- Verify you're logged in
- Check that administrator has assigned you to systems
- Ensure you have talkgroup access within those systems
- Contact your system administrator if needed

**Audio won't play:**

- Check browser audio permissions
- Verify audio files are accessible
- Try refreshing the page
- Check your internet connection

**Scan lists not working:**

- Ensure scan list contains accessible talkgroups
- Verify scan list is marked as Active
- Check that you still have access to included talkgroups
- Try recreating the scan list

**Menu items missing:**

- Check if talkgroups are still accessible to you
- Verify menu preferences haven't been reset
- Ensure talkgroups are marked to show in menu
- Clear browser cache and reload

Getting Help
~~~~~~~~~~~~

**Support Resources:**

1. **Documentation**: Review this user guide and FAQ
2. **Administrator**: Contact your system administrator for access issues
3. **Community**: Join the Trunk Player Google Group for community support
4. **Technical Issues**: Report bugs via GitHub issues

**When Reporting Issues:**

- Describe what you were trying to do
- Include any error messages
- Note your browser and operating system
- Mention which talkgroups or systems are affected
- Include steps to reproduce the problem

**Contact Information:**

- System Administrator: [Contact your local admin]
- Community Forum: `Trunk Player Google Group <https://groups.google.com/forum/#!forum/trunk-player>`_
- Bug Reports: `GitHub Issues <https://github.com/ScanOC/trunk-player/issues>`_