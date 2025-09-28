"""
Tests for the fine-grained authorization system
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import (
    System, TalkGroupWithSystem, SystemRole, SystemPermission,
    UserTalkgroupAccess, UserTalkgroupMenu, UserScanList, Agency
)
from ..auth import (
    has_system_role, has_system_permission, has_talkgroup_access,
    get_user_accessible_talkgroups, create_system_admin,
    grant_talkgroup_access, SystemPermission as SP
)


class SystemRoleTestCase(TestCase):
    """Test system roles and permissions"""

    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass')
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'pass')
        self.no_access_user = User.objects.create_user('noauth', 'noauth@test.com', 'pass')

        # Create test systems
        self.system1 = System.objects.create(name='System 1', system_id='SYS1')
        self.system2 = System.objects.create(name='System 2', system_id='SYS2')

        # Create test agency
        self.agency = Agency.objects.create(name='Test Agency', short='TEST')

        # Create test talkgroups
        self.tg1_sys1 = TalkGroupWithSystem.objects.create(
            dec_id=1001, alpha_tag='TG1-SYS1', description='Test TG 1 System 1',
            system=self.system1, agency=self.agency
        )
        self.tg2_sys1 = TalkGroupWithSystem.objects.create(
            dec_id=1002, alpha_tag='TG2-SYS1', description='Test TG 2 System 1',
            system=self.system1, agency=self.agency
        )
        self.tg1_sys2 = TalkGroupWithSystem.objects.create(
            dec_id=2001, alpha_tag='TG1-SYS2', description='Test TG 1 System 2',
            system=self.system2, agency=self.agency
        )

        # Create system roles
        self.admin_role_sys1 = SystemRole.objects.create(
            user=self.admin_user, system=self.system1, role=SystemRole.ADMIN
        )
        self.user_role_sys1 = SystemRole.objects.create(
            user=self.regular_user, system=self.system1, role=SystemRole.USER
        )
        self.user_role_sys2 = SystemRole.objects.create(
            user=self.regular_user, system=self.system2, role=SystemRole.USER
        )

    def test_system_admin_has_access_to_all_talkgroups(self):
        """System admins should have access to all talkgroups in their system"""
        self.assertTrue(has_system_role(self.admin_user, self.system1, 'admin'))
        self.assertTrue(has_talkgroup_access(self.admin_user, self.tg1_sys1))
        self.assertTrue(has_talkgroup_access(self.admin_user, self.tg2_sys1))

        # But not to other systems
        self.assertFalse(has_system_role(self.admin_user, self.system2))
        self.assertFalse(has_talkgroup_access(self.admin_user, self.tg1_sys2))

    def test_regular_user_needs_explicit_talkgroup_access(self):
        """Regular users need explicit talkgroup access"""
        self.assertTrue(has_system_role(self.regular_user, self.system1, 'user'))

        # No access without explicit grant
        self.assertFalse(has_talkgroup_access(self.regular_user, self.tg1_sys1))

        # Grant access to specific talkgroup
        UserTalkgroupAccess.objects.create(
            user=self.regular_user,
            talkgroup=self.tg1_sys1,
            system_role=self.user_role_sys1
        )

        # Now should have access
        self.assertTrue(has_talkgroup_access(self.regular_user, self.tg1_sys1))
        # But not to other talkgroups
        self.assertFalse(has_talkgroup_access(self.regular_user, self.tg2_sys1))

    def test_user_without_system_role_has_no_access(self):
        """Users without any system role should have no access"""
        self.assertFalse(has_system_role(self.no_access_user, self.system1))
        self.assertFalse(has_talkgroup_access(self.no_access_user, self.tg1_sys1))

    def test_get_user_accessible_talkgroups(self):
        """Test getting all accessible talkgroups for a user"""
        # Admin gets all talkgroups in their system
        admin_tgs = get_user_accessible_talkgroups(self.admin_user, self.system1)
        self.assertEqual(admin_tgs.count(), 2)
        self.assertIn(self.tg1_sys1, admin_tgs)
        self.assertIn(self.tg2_sys1, admin_tgs)

        # Regular user gets only explicitly granted talkgroups
        regular_tgs = get_user_accessible_talkgroups(self.regular_user)
        self.assertEqual(regular_tgs.count(), 0)

        # Grant access to one talkgroup
        UserTalkgroupAccess.objects.create(
            user=self.regular_user,
            talkgroup=self.tg1_sys1,
            system_role=self.user_role_sys1
        )

        regular_tgs = get_user_accessible_talkgroups(self.regular_user)
        self.assertEqual(regular_tgs.count(), 1)
        self.assertIn(self.tg1_sys1, regular_tgs)

    def test_system_permissions(self):
        """Test specific system permissions"""
        # Admin gets all permissions automatically
        self.assertTrue(has_system_permission(self.admin_user, self.system1, SP.EDIT_TALKGROUPS))
        self.assertTrue(has_system_permission(self.admin_user, self.system1, SP.EDIT_UNITS))

        # Regular user has no permissions by default
        self.assertFalse(has_system_permission(self.regular_user, self.system1, SP.EDIT_TALKGROUPS))

        # Grant specific permission
        SystemPermission.objects.create(
            system_role=self.user_role_sys1,
            permission=SP.EDIT_TALKGROUPS
        )

        self.assertTrue(has_system_permission(self.regular_user, self.system1, SP.EDIT_TALKGROUPS))
        # But not other permissions
        self.assertFalse(has_system_permission(self.regular_user, self.system1, SP.EDIT_UNITS))


class APIAuthorizationTestCase(APITestCase):
    """Test API endpoints with authorization"""

    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass')
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'pass')
        self.no_access_user = User.objects.create_user('noauth', 'noauth@test.com', 'pass')

        # Create test system and talkgroups
        self.system = System.objects.create(name='Test System', system_id='TEST')
        self.agency = Agency.objects.create(name='Test Agency', short='TEST')

        self.tg1 = TalkGroupWithSystem.objects.create(
            dec_id=1001, alpha_tag='TG1', description='Test TG 1',
            system=self.system, agency=self.agency
        )
        self.tg2 = TalkGroupWithSystem.objects.create(
            dec_id=1002, alpha_tag='TG2', description='Test TG 2',
            system=self.system, agency=self.agency
        )

        # Create system roles
        self.admin_role = SystemRole.objects.create(
            user=self.admin_user, system=self.system, role=SystemRole.ADMIN
        )
        self.user_role = SystemRole.objects.create(
            user=self.regular_user, system=self.system, role=SystemRole.USER
        )

        # Grant regular user access to one talkgroup
        UserTalkgroupAccess.objects.create(
            user=self.regular_user,
            talkgroup=self.tg1,
            system_role=self.user_role
        )

    def test_talkgroups_api_requires_authentication(self):
        """Talkgroups API should require authentication"""
        response = self.client.get('/api_v1/talkgroups/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_talkgroups_api_filters_by_access(self):
        """Talkgroups API should only return accessible talkgroups"""
        # Admin sees all talkgroups
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api_v1/talkgroups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Regular user sees only accessible talkgroups
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api_v1/talkgroups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['alpha_tag'], 'TG1')

        # User with no access sees nothing
        self.client.force_authenticate(user=self.no_access_user)
        response = self.client.get('/api_v1/talkgroups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_transmissions_api_filters_by_talkgroup_access(self):
        """Transmissions API should only return transmissions from accessible talkgroups"""
        from ..models import Transmission

        # Create test transmissions
        trans1 = Transmission.objects.create(
            audio_file='test1.wav',
            talkgroup_info=self.tg1,
            system=self.system
        )
        trans2 = Transmission.objects.create(
            audio_file='test2.wav',
            talkgroup_info=self.tg2,
            system=self.system
        )

        # Admin sees all transmissions
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api_v1/transmission/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Regular user sees only transmissions from accessible talkgroups
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api_v1/transmission/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class UserPreferencesTestCase(TestCase):
    """Test user menu and scan list preferences"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.system = System.objects.create(name='Test System', system_id='TEST')
        self.agency = Agency.objects.create(name='Test Agency', short='TEST')

        self.tg1 = TalkGroupWithSystem.objects.create(
            dec_id=1001, alpha_tag='TG1', description='Test TG 1',
            system=self.system, agency=self.agency
        )
        self.tg2 = TalkGroupWithSystem.objects.create(
            dec_id=1002, alpha_tag='TG2', description='Test TG 2',
            system=self.system, agency=self.agency
        )

        # Give user access to talkgroups
        self.user_role = SystemRole.objects.create(
            user=self.user, system=self.system, role=SystemRole.USER
        )
        UserTalkgroupAccess.objects.create(
            user=self.user, talkgroup=self.tg1, system_role=self.user_role
        )
        UserTalkgroupAccess.objects.create(
            user=self.user, talkgroup=self.tg2, system_role=self.user_role
        )

    def test_talkgroup_menu_management(self):
        """Test managing talkgroup menu visibility"""
        # Initially no menu settings
        self.assertEqual(UserTalkgroupMenu.objects.filter(user=self.user).count(), 0)

        # Create menu setting
        menu_item = UserTalkgroupMenu.objects.create(
            user=self.user,
            talkgroup=self.tg1,
            show_in_menu=True,
            order=1
        )

        self.assertTrue(menu_item.show_in_menu)
        self.assertEqual(menu_item.order, 1)

        # Test unique constraint (user + talkgroup)
        with self.assertRaises(Exception):
            UserTalkgroupMenu.objects.create(
                user=self.user,
                talkgroup=self.tg1,
                show_in_menu=False
            )

    def test_user_scan_lists(self):
        """Test user custom scan lists"""
        # Create scan list
        scan_list = UserScanList.objects.create(
            user=self.user,
            name='My Scan List',
            description='Test scan list',
            is_default=True
        )
        scan_list.talkgroups.add(self.tg1, self.tg2)

        self.assertEqual(scan_list.talkgroups.count(), 2)
        self.assertTrue(scan_list.is_default)

        # Test unique constraint (user + name)
        with self.assertRaises(Exception):
            UserScanList.objects.create(
                user=self.user,
                name='My Scan List'
            )

        # Test default scan list enforcement
        scan_list2 = UserScanList.objects.create(
            user=self.user,
            name='Another List',
            is_default=True
        )

        # First scan list should no longer be default
        scan_list.refresh_from_db()
        self.assertFalse(scan_list.is_default)
        self.assertTrue(scan_list2.is_default)


class AuthHelperFunctionsTestCase(TestCase):
    """Test auth helper functions"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.system = System.objects.create(name='Test System', system_id='TEST')
        self.agency = Agency.objects.create(name='Test Agency', short='TEST')

        self.tg = TalkGroupWithSystem.objects.create(
            dec_id=1001, alpha_tag='TG1', description='Test TG 1',
            system=self.system, agency=self.agency
        )

    def test_create_system_admin(self):
        """Test creating system admin role"""
        admin_role = create_system_admin(self.user, self.system)

        self.assertEqual(admin_role.user, self.user)
        self.assertEqual(admin_role.system, self.system)
        self.assertEqual(admin_role.role, SystemRole.ADMIN)
        self.assertTrue(admin_role.is_admin)

    def test_grant_talkgroup_access(self):
        """Test granting talkgroup access"""
        access = grant_talkgroup_access(self.user, self.tg)

        self.assertEqual(access.user, self.user)
        self.assertEqual(access.talkgroup, self.tg)
        self.assertTrue(has_talkgroup_access(self.user, self.tg))

        # Should also create system role if it doesn't exist
        self.assertTrue(SystemRole.objects.filter(user=self.user, system=self.system).exists())

    def test_anonymous_user_has_no_access(self):
        """Test that anonymous users have no access"""
        from django.contrib.auth.models import AnonymousUser

        anon_user = AnonymousUser()
        self.assertFalse(has_system_role(anon_user, self.system))
        self.assertFalse(has_talkgroup_access(anon_user, self.tg))
        self.assertEqual(get_user_accessible_talkgroups(anon_user).count(), 0)