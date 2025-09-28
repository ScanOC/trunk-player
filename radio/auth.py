"""
Fine-grained authorization system for Trunk Player
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import SystemRole, SystemPermission, UserTalkgroupAccess, System, TalkGroupWithSystem


class TrunkPlayerPermissionError(Exception):
    """Custom exception for permission errors"""
    pass


def require_authentication(view_func):
    """
    Decorator to require authentication for all views unless ALLOW_ANONYMOUS is True
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if anonymous access is allowed
        if getattr(settings, 'ALLOW_ANONYMOUS', False):
            return view_func(request, *args, **kwargs)

        # Require authentication
        if not request.user.is_authenticated:
            if request.content_type == 'application/json' or 'api' in request.path:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

        return view_func(request, *args, **kwargs)

    return wrapper


def require_system_role(required_role='user', system_param='system_id'):
    """
    Decorator to require a specific role within a system

    Args:
        required_role: 'admin' or 'user' (default: 'user')
        system_param: parameter name containing system ID (default: 'system_id')
    """
    def decorator(view_func):
        @wraps(view_func)
        @require_authentication
        def wrapper(request, *args, **kwargs):
            # Get system from request parameters
            system_id = kwargs.get(system_param) or request.GET.get('system') or request.POST.get('system')

            if not system_id:
                # Try to get system from talkgroup or other related objects
                tg_id = kwargs.get('talkgroup_id') or request.GET.get('talkgroup')
                if tg_id:
                    try:
                        tg = TalkGroupWithSystem.objects.get(pk=tg_id)
                        system_id = tg.system.pk
                    except TalkGroupWithSystem.DoesNotExist:
                        raise PermissionDenied("Talkgroup not found")

            if not system_id:
                raise PermissionDenied("System not specified")

            system = get_object_or_404(System, pk=system_id)

            # Check if user has required role in this system
            try:
                system_role = SystemRole.objects.get(user=request.user, system=system)
                if required_role == 'admin' and not system_role.is_admin:
                    raise PermissionDenied("System administrator access required")
            except SystemRole.DoesNotExist:
                raise PermissionDenied("Access to this system not granted")

            # Add system and role to request for use in view
            request.system = system
            request.system_role = system_role

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_system_permission(permission):
    """
    Decorator to require a specific permission within a system

    Args:
        permission: Permission constant from SystemPermission model
    """
    def decorator(view_func):
        @wraps(view_func)
        @require_system_role()
        def wrapper(request, *args, **kwargs):
            # Check if user has the specific permission
            if not has_system_permission(request.user, request.system, permission):
                raise PermissionDenied(f"Permission '{permission}' required")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_talkgroup_access(view_func):
    """
    Decorator to require access to a specific talkgroup
    """
    @wraps(view_func)
    @require_authentication
    def wrapper(request, *args, **kwargs):
        # Get talkgroup from request
        tg_id = kwargs.get('talkgroup_id') or kwargs.get('pk') or request.GET.get('talkgroup')

        if not tg_id:
            raise PermissionDenied("Talkgroup not specified")

        talkgroup = get_object_or_404(TalkGroupWithSystem, pk=tg_id)

        # Check if user has access to this talkgroup
        if not has_talkgroup_access(request.user, talkgroup):
            raise PermissionDenied("Access to this talkgroup not granted")

        # Add talkgroup to request for use in view
        request.talkgroup = talkgroup

        return view_func(request, *args, **kwargs)

    return wrapper


# Utility functions for checking permissions

def has_system_role(user, system, role='user'):
    """Check if user has a specific role in a system"""
    if not user.is_authenticated:
        return False

    try:
        system_role = SystemRole.objects.get(user=user, system=system)
        if role == 'admin':
            return system_role.is_admin
        return True  # Has any role
    except SystemRole.DoesNotExist:
        return False


def has_system_permission(user, system, permission):
    """Check if user has a specific permission in a system"""
    if not user.is_authenticated:
        return False

    try:
        system_role = SystemRole.objects.get(user=user, system=system)

        # Admins automatically get all permissions
        if system_role.is_admin:
            return True

        # Check specific permission
        return SystemPermission.objects.filter(
            system_role=system_role,
            permission=permission
        ).exists()
    except SystemRole.DoesNotExist:
        return False


def has_talkgroup_access(user, talkgroup):
    """Check if user has access to a specific talkgroup"""
    if not user.is_authenticated:
        return False

    # Check if user has system role first
    if not has_system_role(user, talkgroup.system):
        return False

    # System admins get access to all talkgroups
    system_role = SystemRole.objects.get(user=user, system=talkgroup.system)
    if system_role.is_admin:
        return True

    # Check specific talkgroup access
    return UserTalkgroupAccess.objects.filter(
        user=user,
        talkgroup=talkgroup
    ).exists()


def get_user_accessible_talkgroups(user, system=None):
    """Get all talkgroups a user has access to"""
    if not user.is_authenticated:
        return TalkGroupWithSystem.objects.none()

    accessible_tgs = TalkGroupWithSystem.objects.none()

    # Get user's system roles
    system_roles = SystemRole.objects.filter(user=user)
    if system:
        system_roles = system_roles.filter(system=system)

    for system_role in system_roles:
        if system_role.is_admin:
            # Admins get all talkgroups in their systems
            system_tgs = TalkGroupWithSystem.objects.filter(system=system_role.system)
            accessible_tgs = accessible_tgs.union(system_tgs)
        else:
            # Regular users get explicitly granted talkgroups
            user_tgs = TalkGroupWithSystem.objects.filter(
                user_permissions__user=user,
                system=system_role.system
            )
            accessible_tgs = accessible_tgs.union(user_tgs)

    return accessible_tgs


def get_user_systems(user):
    """Get all systems a user has access to"""
    if not user.is_authenticated:
        return System.objects.none()

    return System.objects.filter(user_roles__user=user).distinct()


def create_system_admin(user, system, created_by=None):
    """Create a system admin role for a user"""
    system_role, created = SystemRole.objects.get_or_create(
        user=user,
        system=system,
        defaults={
            'role': SystemRole.ADMIN,
            'created_by': created_by
        }
    )

    if not created and system_role.role != SystemRole.ADMIN:
        system_role.role = SystemRole.ADMIN
        system_role.save()

    return system_role


def grant_talkgroup_access(user, talkgroup, granted_by=None):
    """Grant a user access to a specific talkgroup"""
    # Ensure user has a role in the system first
    system_role, created = SystemRole.objects.get_or_create(
        user=user,
        system=talkgroup.system,
        defaults={
            'role': SystemRole.USER,
            'created_by': granted_by
        }
    )

    # Grant talkgroup access
    access, created = UserTalkgroupAccess.objects.get_or_create(
        user=user,
        talkgroup=talkgroup,
        defaults={
            'system_role': system_role,
            'granted_by': granted_by
        }
    )

    return access


def revoke_talkgroup_access(user, talkgroup):
    """Revoke a user's access to a specific talkgroup"""
    UserTalkgroupAccess.objects.filter(
        user=user,
        talkgroup=talkgroup
    ).delete()