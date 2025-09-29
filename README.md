Trunk Player
============

### Version 0.1.5 - Fine-Grained Authorization Update

Python Django web frontend for playing recorded radio transmissions with comprehensive user authorization and access control. The audio files are recorded using [Trunk Recorder](https://github.com/robotastic/trunk-recorder).

![Main Screen](/../master/docs/images/trunk_player_main.png?raw=true "Main Screen")

## 🆕 What's New in v0.1.5

- **Fine-Grained Authorization System**: Multi-system user management with role-based access control
- **User-Specific Scan Lists**: Create and manage personal scan lists with talkgroup selections
- **Menu Customization**: Users can customize which talkgroups appear in their personal menu
- **System-Level Access Control**: Users can have different roles (admin/user) across multiple radio systems
- **Enhanced Security**: All API endpoints now require authentication and filter data by user permissions
- **Unique Slug System**: Improved URL routing with system-prefixed unique identifiers

## 🔐 Authorization System Features

### Multi-System Access Control
- **System Roles**: Users can be assigned Admin or Regular User roles per radio system
- **Cross-System Access**: Single users can access multiple radio systems with different permission levels
- **Permission Granularity**: Control over talkgroup access, unit editing, and system management per system

### User Management
- **System Administrators**: Can manage users, assign talkgroup access, and configure system settings
- **Regular Users**: Access only assigned talkgroups and can manage personal preferences
- **Automatic Access**: System admins automatically get access to all talkgroups in their systems

### Personal Customization
- **Custom Scan Lists**: Users create named scan lists from their accessible talkgroups
- **Menu Preferences**: Flag specific talkgroups to appear in personal navigation menu
- **Default Scan Lists**: Set preferred scan list for quick access

## 🔧 Build and Install
  Documents are at Read the Docs [http://trunk-player.readthedocs.io/](http://trunk-player.readthedocs.io/)

  Checkout some install notes in the WIKI also https://github.com/ScanOC/trunk-player/wiki

### Quick Start with Docker
```bash
git clone https://github.com/ScanOC/trunk-player.git
cd trunk-player
docker compose up -d
```

### Post-Installation Setup
1. **Create Admin User**: Access Django admin to create your first system administrator
2. **Configure Systems**: Add radio systems and assign system administrators
3. **Import Talkgroups**: Add talkgroups to systems via admin interface
4. **Assign User Access**: System admins can grant talkgroup access to users

## Support
 There is a google groups mailing list [Trunk Player](https://groups.google.com/forum/#!forum/trunk-player)

## Using with Unitrunker/EDACS Systems
Check out https://github.com/MaxwellDPS/Unibridge for using Trunk-Player with unitrunker

## License
 - Trunk Player is licensed under the [MIT License](License.txt)

## WIP
 - The code still has a lot of work. If you have issues or question feel free to post in the google group.

## Discuss
 [![Gitter](https://badges.gitter.im/TrunkPlayer/Lobby.svg)](https://gitter.im/TrunkPlayer/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
