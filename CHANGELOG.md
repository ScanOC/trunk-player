# Changelog

All notable changes to Trunk Player will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2024-01-XX

### 🆕 Added

#### Fine-Grained Authorization System
- **Multi-System User Management**: Users can now have different roles across multiple radio systems
- **System Roles**: Two-tier role system (System Administrator, Regular User) per radio system
- **Granular Permissions**: Control over talkgroup access, unit editing, and system management
- **User Talkgroup Access**: System admins can assign specific talkgroup access to regular users
- **Automatic Admin Access**: System administrators automatically get access to all talkgroups in their systems

#### Personal User Features
- **Custom Scan Lists**: Users can create named scan lists from their accessible talkgroups
- **Menu Customization**: Flag specific talkgroups to appear in personal navigation menu
- **Default Scan Lists**: Set preferred scan list for automatic selection
- **Personal Preferences**: User-specific settings for menu order and scan list organization

#### Enhanced Security
- **Authenticated APIs**: All API endpoints now require user authentication
- **Permission-Filtered Data**: API responses filtered based on user's system access
- **Secure ViewSets**: Complete rewrite of API endpoints with authentication and permission checks
- **Access Control**: Granular control over who can view, edit, and manage system data

#### Unique Slug System
- **System-Prefixed Slugs**: TalkGroup slugs now include system prefix (e.g., `sys1-police-dispatch`)
- **User-Prefixed Scan Lists**: UserScanList slugs include user prefix (e.g., `user5-emergency-services`)
- **Global Uniqueness**: All slugs are now globally unique across systems and users
- **Improved URL Routing**: Better URL structure with conflict-free routing

### 🔧 Changed

#### API Breaking Changes
- **Authentication Required**: Anonymous access now controlled by `ALLOW_ANONYMOUS` setting
- **Filtered Responses**: All API endpoints return only data accessible to authenticated user
- **New Slug Format**: TalkGroup slugs changed from `alpha-tag` to `sys{id}-alpha-tag`
- **Endpoint Behavior**: `/api_v1/menutalkgrouplist/` and `/api_v1/menuscanlist/` now user-specific

#### Database Schema
- **New Models**: SystemRole, SystemPermission, UserTalkgroupAccess, UserTalkgroupMenu, UserScanList
- **Enhanced Indexes**: Improved database performance for permission queries
- **Unique Constraints**: Added unique constraints to slug fields
- **Migration Path**: Automatic migration preserves existing data

#### User Interface
- **Simplified Talkgroup List**: Removed Common Name, Agency, Notes, and Toggle columns
- **Enhanced Management Pages**: New interfaces for menu management and scan list creation
- **User System Overview**: New page showing user's system access and roles
- **Streamlined Templates**: Cleaner, more focused user interfaces

### 🚀 Improved

#### Performance
- **Optimized Queries**: Database queries optimized for permission checking
- **Efficient Filtering**: Improved performance for large talkgroup lists
- **Better Indexing**: Strategic database indexes for authorization queries

#### User Experience
- **Intuitive Navigation**: Clearer separation between personal and system features
- **Bulk Operations**: Bulk menu management and scan list operations
- **AJAX Interactions**: Smoother user interactions with real-time updates
- **Better Error Handling**: Improved error messages and user feedback

#### Documentation
- **Comprehensive Guides**: New documentation for authorization system
- **API Documentation**: Complete API reference with examples
- **Upgrade Guide**: Detailed migration instructions
- **Best Practices**: Guidelines for system administration and user management

### 🐛 Fixed

#### Security Issues
- **Data Leakage Prevention**: Eliminated unauthorized access to talkgroup data
- **Permission Bypass**: Fixed potential permission bypass in API endpoints
- **Cross-System Access**: Prevented users from accessing unauthorized systems

#### Functional Issues
- **Scan List URLs**: Fixed scan list URL generation to use proper slugs
- **Menu Synchronization**: Improved menu state synchronization across sessions
- **Template Missing**: Fixed missing template errors for user preference pages

### 📋 Technical Details

#### New Models
```python
# Core authorization models
SystemRole           # User roles per system
SystemPermission     # Granular permissions
UserTalkgroupAccess  # Specific talkgroup access
UserTalkgroupMenu    # Personal menu preferences
UserScanList         # Custom user scan lists
```

#### New API Endpoints
- `/api_v1/menutalkgrouplist/` - User's menu talkgroups (now user-specific)
- `/api_v1/menuscanlist/` - User's scan lists (now user-specific)
- `/api_v1/scan/{slug}/` - Enhanced scan list filtering with slug support

#### New Management URLs
- `/manage/menu/` - Bulk talkgroup menu management
- `/manage/scan-lists/` - User scan list management
- `/talkgroups/manage/` - Individual talkgroup menu toggles
- `/user/systems/` - User system access overview

#### Database Migrations
- `0063_add_fine_grained_auth.py` - Core authorization system
- `0064_update_slugs_for_uniqueness.py` - Slug prefix system
- `0065_make_slugs_unique.py` - Unique constraints

### ⚠️ Breaking Changes

#### For Administrators
- **User Access**: All existing users need to be assigned to systems to maintain access
- **API Changes**: API clients must be updated to handle authentication
- **URL Changes**: TalkGroup URLs now use system-prefixed slugs

#### For Developers
- **Model Changes**: New authorization models affect data access patterns
- **API Authentication**: All API endpoints require authentication
- **Slug Format**: Update any code that relies on TalkGroup slug format

### 🔄 Migration Guide

1. **Backup Database**: Always backup before upgrading
2. **Run Migrations**: `python manage.py migrate radio`
3. **Assign System Roles**: Create system administrators via Django admin
4. **Configure Access**: Assign users to systems and talkgroups
5. **Update API Clients**: Add authentication to API requests
6. **Test Functionality**: Verify all features work as expected

### 📚 Documentation Updates

- **New Authorization Guide**: Comprehensive documentation for fine-grained access control
- **API Reference**: Complete API documentation with authentication examples
- **Upgrade Instructions**: Detailed migration guide for existing installations
- **Best Practices**: Guidelines for system administration and security

---

## [0.1.4] - Previous Release

### Features
- Basic talkgroup and transmission management
- Public scan lists
- Basic user authentication
- Simple API endpoints

### Known Issues
- No fine-grained access control
- All authenticated users could access all data
- Limited user customization options
- Basic authorization system

---

## Contributing

When adding entries to this changelog:

1. **Use semantic versioning** for release numbers
2. **Group changes** by type (Added, Changed, Improved, Fixed, etc.)
3. **Be specific** about what changed and why
4. **Include breaking changes** with clear migration paths
5. **Reference issues/PRs** when applicable

### Change Types

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes