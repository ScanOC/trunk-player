"""
User preference management views for menu flags and scan lists
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import UserTalkgroupMenu, UserScanList, TalkGroupWithSystem
from .auth import get_user_accessible_talkgroups, has_talkgroup_access
from .forms import UserScanListForm


@login_required
def manage_talkgroup_menu(request):
    """
    View for users to manage which talkgroups show in their menu
    """
    # Get all accessible talkgroups for this user
    accessible_tgs = get_user_accessible_talkgroups(request.user)

    # Get current menu settings
    menu_settings = {}
    for menu_item in UserTalkgroupMenu.objects.filter(user=request.user):
        menu_settings[menu_item.talkgroup.id] = {
            'show_in_menu': menu_item.show_in_menu,
            'order': menu_item.order
        }

    # Group talkgroups by system for better organization
    talkgroups_by_system = {}
    for tg in accessible_tgs.select_related('system').order_by('system__name', 'alpha_tag'):
        system_name = tg.system.name
        if system_name not in talkgroups_by_system:
            talkgroups_by_system[system_name] = []

        talkgroups_by_system[system_name].append({
            'talkgroup': tg,
            'menu_settings': menu_settings.get(tg.id, {'show_in_menu': False, 'order': 0})
        })

    if request.method == 'POST':
        # Handle bulk update of menu settings
        talkgroup_ids = request.POST.getlist('talkgroup_ids[]')
        show_flags = request.POST.getlist('show_in_menu[]')
        orders = request.POST.getlist('order[]')

        # Clear existing menu settings for this user
        UserTalkgroupMenu.objects.filter(user=request.user).delete()

        # Create new menu settings
        for i, tg_id in enumerate(talkgroup_ids):
            try:
                tg = accessible_tgs.get(id=int(tg_id))
                show_in_menu = i < len(show_flags) and show_flags[i] == 'on'
                order = int(orders[i]) if i < len(orders) and orders[i].isdigit() else 0

                if show_in_menu or order > 0:  # Only create if there's a setting to save
                    UserTalkgroupMenu.objects.create(
                        user=request.user,
                        talkgroup=tg,
                        show_in_menu=show_in_menu,
                        order=order
                    )
            except (ValueError, TalkGroupWithSystem.DoesNotExist):
                continue

        return redirect('manage_talkgroup_menu')

    return render(request, 'radio/manage_talkgroup_menu.html', {
        'talkgroups_by_system': talkgroups_by_system,
        'user': request.user
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def toggle_talkgroup_menu(request):
    """
    AJAX endpoint to toggle a single talkgroup's menu visibility
    """
    try:
        data = json.loads(request.body)
        talkgroup_id = data.get('talkgroup_id')

        if not talkgroup_id:
            return JsonResponse({'error': 'Talkgroup ID required'}, status=400)

        # Get the talkgroup and verify user has access
        accessible_tgs = get_user_accessible_talkgroups(request.user)
        talkgroup = get_object_or_404(accessible_tgs, id=talkgroup_id)

        # Toggle menu setting
        menu_item, created = UserTalkgroupMenu.objects.get_or_create(
            user=request.user,
            talkgroup=talkgroup,
            defaults={'show_in_menu': True, 'order': 0}
        )

        if not created:
            menu_item.show_in_menu = not menu_item.show_in_menu
            menu_item.save()

        return JsonResponse({
            'success': True,
            'talkgroup_id': talkgroup_id,
            'show_in_menu': menu_item.show_in_menu
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def manage_scan_lists(request):
    """
    View for users to manage their custom scan lists
    """
    scan_lists = UserScanList.objects.filter(user=request.user).order_by('name')

    return render(request, 'radio/manage_scan_lists.html', {
        'scan_lists': scan_lists,
        'user': request.user
    })


@login_required
def create_scan_list(request):
    """
    View to create a new user scan list
    """
    accessible_tgs = get_user_accessible_talkgroups(request.user)

    # Group talkgroups by system for better UX
    talkgroups_by_system = {}
    for tg in accessible_tgs.select_related('system').order_by('system__name', 'alpha_tag'):
        system_name = tg.system.name
        if system_name not in talkgroups_by_system:
            talkgroups_by_system[system_name] = []
        talkgroups_by_system[system_name].append(tg)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        talkgroup_ids = request.POST.getlist('talkgroups')
        is_default = request.POST.get('is_default') == 'on'

        if not name:
            return render(request, 'radio/create_scan_list.html', {
                'error': 'Scan list name is required',
                'talkgroups_by_system': talkgroups_by_system,
                'form_data': request.POST
            })

        # Check if user already has a scan list with this name
        if UserScanList.objects.filter(user=request.user, name=name).exists():
            return render(request, 'radio/create_scan_list.html', {
                'error': 'You already have a scan list with this name',
                'talkgroups_by_system': talkgroups_by_system,
                'form_data': request.POST
            })

        # Verify all selected talkgroups are accessible
        selected_tgs = accessible_tgs.filter(id__in=talkgroup_ids)

        # Create scan list
        scan_list = UserScanList.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_default=is_default
        )
        scan_list.talkgroups.set(selected_tgs)

        return redirect('manage_scan_lists')

    return render(request, 'radio/create_scan_list.html', {
        'talkgroups_by_system': talkgroups_by_system
    })


@login_required
def edit_scan_list(request, scan_list_id):
    """
    View to edit an existing user scan list
    """
    scan_list = get_object_or_404(UserScanList, id=scan_list_id, user=request.user)
    accessible_tgs = get_user_accessible_talkgroups(request.user)

    # Group talkgroups by system
    talkgroups_by_system = {}
    selected_tg_ids = set(scan_list.talkgroups.values_list('id', flat=True))

    for tg in accessible_tgs.select_related('system').order_by('system__name', 'alpha_tag'):
        system_name = tg.system.name
        if system_name not in talkgroups_by_system:
            talkgroups_by_system[system_name] = []
        talkgroups_by_system[system_name].append({
            'talkgroup': tg,
            'selected': tg.id in selected_tg_ids
        })

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        talkgroup_ids = request.POST.getlist('talkgroups')
        is_default = request.POST.get('is_default') == 'on'

        if not name:
            return render(request, 'radio/edit_scan_list.html', {
                'error': 'Scan list name is required',
                'scan_list': scan_list,
                'talkgroups_by_system': talkgroups_by_system,
                'form_data': request.POST
            })

        # Check if name conflicts with another scan list
        existing = UserScanList.objects.filter(user=request.user, name=name).exclude(id=scan_list.id)
        if existing.exists():
            return render(request, 'radio/edit_scan_list.html', {
                'error': 'You already have a scan list with this name',
                'scan_list': scan_list,
                'talkgroups_by_system': talkgroups_by_system,
                'form_data': request.POST
            })

        # Update scan list
        scan_list.name = name
        scan_list.description = description
        scan_list.is_default = is_default
        scan_list.save()

        # Update talkgroups
        selected_tgs = accessible_tgs.filter(id__in=talkgroup_ids)
        scan_list.talkgroups.set(selected_tgs)

        return redirect('manage_scan_lists')

    return render(request, 'radio/edit_scan_list.html', {
        'scan_list': scan_list,
        'talkgroups_by_system': talkgroups_by_system
    })


@login_required
def delete_scan_list(request, scan_list_id):
    """
    View to delete a user scan list
    """
    scan_list = get_object_or_404(UserScanList, id=scan_list_id, user=request.user)

    if request.method == 'POST':
        scan_list.delete()
        return redirect('manage_scan_lists')

    return render(request, 'radio/delete_scan_list.html', {
        'scan_list': scan_list
    })


@login_required
def user_systems_view(request):
    """
    View showing all systems the user has access to and their roles
    """
    from .models import SystemRole
    from .auth import get_user_systems

    user_systems = []
    for system_role in SystemRole.objects.filter(user=request.user).select_related('system'):
        accessible_tgs = get_user_accessible_talkgroups(request.user, system=system_role.system)
        user_systems.append({
            'system': system_role.system,
            'role': system_role,
            'talkgroup_count': accessible_tgs.count(),
            'is_admin': system_role.is_admin
        })

    return render(request, 'radio/user_systems.html', {
        'user_systems': user_systems
    })


@login_required
def talkgroup_list_with_menu_flags(request):
    """
    Enhanced talkgroup list showing menu flag status for each talkgroup
    """
    accessible_tgs = get_user_accessible_talkgroups(request.user)

    # Get menu settings
    menu_settings = {}
    for menu_item in UserTalkgroupMenu.objects.filter(user=request.user):
        menu_settings[menu_item.talkgroup.id] = menu_item

    # Paginate results
    paginator = Paginator(accessible_tgs.select_related('system').order_by('system__name', 'alpha_tag'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add menu settings to each talkgroup
    talkgroups_with_menu = []
    for tg in page_obj:
        menu_item = menu_settings.get(tg.id)
        talkgroups_with_menu.append({
            'talkgroup': tg,
            'show_in_menu': menu_item.show_in_menu if menu_item else False,
            'menu_order': menu_item.order if menu_item else 0
        })

    return render(request, 'radio/talkgroup_list_with_menu.html', {
        'talkgroups_with_menu': talkgroups_with_menu,
        'page_obj': page_obj,
        'paginator': paginator
    })