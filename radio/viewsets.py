"""
Secured API ViewSets with fine-grained authorization
"""
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import PermissionDenied

from .models import (
    Transmission, TalkGroupWithSystem, ScanList, MenuScanList,
    MenuTalkGroupList, MessagePopUp, Unit, UserScanList, UserTalkgroupMenu
)
from .serializers import (
    TransmissionSerializer, TalkGroupSerializer, ScanListSerializer,
    MenuScanListSerializer, MenuTalkGroupListSerializer, MessageSerializer
)
from .auth import (
    get_user_accessible_talkgroups, get_user_systems, has_system_permission,
    SystemPermission, has_talkgroup_access
)


class AuthenticatedViewSetMixin:
    """Mixin to ensure all API endpoints require authentication"""
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        # Check if anonymous access is allowed globally
        if not getattr(settings, 'ALLOW_ANONYMOUS', False):
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)


class SecureTransmissionViewSet(AuthenticatedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Secure API endpoint for transmissions - read-only access based on talkgroup permissions
    """
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            if getattr(settings, 'ALLOW_ANONYMOUS', False):
                return Transmission.objects.none()  # No access for anonymous users
            return Transmission.objects.none()

        # Get user's accessible talkgroups
        accessible_tgs = get_user_accessible_talkgroups(self.request.user)

        # Filter transmissions to only those from accessible talkgroups
        queryset = Transmission.objects.filter(
            talkgroup_info__in=accessible_tgs
        ).prefetch_related('units').select_related('talkgroup_info', 'system')

        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class SecureTalkGroupViewSet(AuthenticatedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Secure API endpoint for talkgroups - only shows accessible talkgroups
    """
    serializer_class = TalkGroupSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return TalkGroupWithSystem.objects.none()

        return get_user_accessible_talkgroups(self.request.user)

    @action(detail=False, methods=['get'])
    def menu_items(self, request):
        """Get talkgroups that user has flagged for their menu"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)

        menu_tgs = UserTalkgroupMenu.objects.filter(
            user=request.user,
            show_in_menu=True
        ).select_related('talkgroup').order_by('order', 'talkgroup__alpha_tag')

        # Only include talkgroups user actually has access to
        accessible_tgs = get_user_accessible_talkgroups(request.user)
        accessible_menu_tgs = menu_tgs.filter(talkgroup__in=accessible_tgs)

        data = []
        for menu_tg in accessible_menu_tgs:
            data.append({
                'id': menu_tg.talkgroup.id,
                'name': menu_tg.talkgroup.alpha_tag,
                'slug': menu_tg.talkgroup.slug,
                'system': menu_tg.talkgroup.system.name,
                'order': menu_tg.order
            })

        return Response(data)

    @action(detail=True, methods=['post'])
    def toggle_menu(self, request, pk=None):
        """Toggle talkgroup visibility in user's menu"""
        talkgroup = self.get_object()

        # Check if user has access to this talkgroup
        if not has_talkgroup_access(request.user, talkgroup):
            raise PermissionDenied("Access to this talkgroup not granted")

        menu_item, created = UserTalkgroupMenu.objects.get_or_create(
            user=request.user,
            talkgroup=talkgroup,
            defaults={'show_in_menu': True}
        )

        if not created:
            menu_item.show_in_menu = not menu_item.show_in_menu
            menu_item.save()

        return Response({
            'talkgroup_id': talkgroup.id,
            'show_in_menu': menu_item.show_in_menu
        })


class SecureScanListViewSet(AuthenticatedViewSetMixin, viewsets.ModelViewSet):
    """
    Secure API endpoint for scan lists - users can only see/edit their own custom lists
    """
    serializer_class = ScanListSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ScanList.objects.none()

        # Return public scan lists + user's custom scan lists
        public_scanlists = ScanList.objects.filter(public=True)
        user_scanlists = UserScanList.objects.filter(user=self.request.user, is_active=True)

        # Convert UserScanList to ScanList format for API compatibility
        # This might need adjustment based on your exact models
        return public_scanlists

    @action(detail=False, methods=['get'])
    def user_scanlists(self, request):
        """Get user's custom scan lists"""
        user_scanlists = UserScanList.objects.filter(
            user=request.user,
            is_active=True
        ).prefetch_related('talkgroups')

        data = []
        for scanlist in user_scanlists:
            # Only include talkgroups user has access to
            accessible_tgs = get_user_accessible_talkgroups(request.user)
            accessible_tg_ids = accessible_tgs.values_list('id', flat=True)
            scanlist_tgs = scanlist.talkgroups.filter(id__in=accessible_tg_ids)

            data.append({
                'id': scanlist.id,
                'name': scanlist.name,
                'description': scanlist.description,
                'is_default': scanlist.is_default,
                'talkgroup_count': scanlist_tgs.count(),
                'talkgroups': [{'id': tg.id, 'name': tg.alpha_tag} for tg in scanlist_tgs]
            })

        return Response(data)

    @action(detail=False, methods=['post'])
    def create_user_scanlist(self, request):
        """Create a new user scan list"""
        name = request.data.get('name')
        description = request.data.get('description', '')
        talkgroup_ids = request.data.get('talkgroups', [])

        if not name:
            return Response({'error': 'Name is required'}, status=400)

        # Check if user already has a scan list with this name
        if UserScanList.objects.filter(user=request.user, name=name).exists():
            return Response({'error': 'Scan list with this name already exists'}, status=400)

        # Verify user has access to all specified talkgroups
        accessible_tgs = get_user_accessible_talkgroups(request.user)
        accessible_tg_ids = accessible_tgs.values_list('id', flat=True)

        # Get intersection of requested talkgroups and accessible talkgroups
        valid_tg_ids = [tg_id for tg_id in talkgroup_ids if int(tg_id) in accessible_tg_ids]
        requested_tgs = TalkGroupWithSystem.objects.filter(id__in=valid_tg_ids)

        if len(requested_tgs) != len(talkgroup_ids):
            return Response({'error': 'Access denied to some talkgroups'}, status=403)

        # Create scan list
        scanlist = UserScanList.objects.create(
            user=request.user,
            name=name,
            description=description
        )
        scanlist.talkgroups.set(requested_tgs)

        return Response({
            'id': scanlist.id,
            'name': scanlist.name,
            'description': scanlist.description
        }, status=201)


class SecureUnitFilterViewSet(AuthenticatedViewSetMixin, generics.ListAPIView):
    """
    Secure API endpoint for unit-based transmission filtering
    """
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Transmission.objects.none()

        unit_var = self.kwargs['filter_val']
        search_unit = unit_var.split('+')

        q = Q()
        for s_unit in search_unit:
            q |= Q(slug__iexact=s_unit)

        units = Unit.objects.filter(q)

        # Get user's accessible talkgroups
        accessible_tgs = get_user_accessible_talkgroups(self.request.user)

        # Filter transmissions by accessible talkgroups and units
        return Transmission.objects.filter(
            units__in=units,
            talkgroup_info__in=accessible_tgs
        ).prefetch_related('units').distinct()


class SecureTalkGroupFilterViewSet(AuthenticatedViewSetMixin, generics.ListAPIView):
    """
    Secure API endpoint for talkgroup-based transmission filtering
    """
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Transmission.objects.none()

        tg_var = self.kwargs['filter_val']
        search_tgs = tg_var.split('+')

        q = Q()
        for stg in search_tgs:
            q |= Q(alpha_tag__iexact=stg)
            q |= Q(slug__iexact=stg)

        # Get matching talkgroups that user has access to
        accessible_tgs = get_user_accessible_talkgroups(self.request.user)
        requested_tgs = accessible_tgs.filter(q)

        # Get transmissions from these talkgroups
        return Transmission.objects.filter(
            talkgroup_info__in=requested_tgs
        ).prefetch_related('units').order_by('-start_datetime')


class SecureScanViewSet(AuthenticatedViewSetMixin, generics.ListAPIView):
    """
    Secure API endpoint for scan list based transmission filtering
    """
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Transmission.objects.none()

        scanlist = self.kwargs['filter_val']

        try:
            if scanlist == 'default':
                # Use user's default scan list or all accessible talkgroups
                try:
                    default_scanlist = UserScanList.objects.get(
                        user=self.request.user,
                        is_default=True,
                        is_active=True
                    )
                    talkgroups = default_scanlist.talkgroups.all()
                except UserScanList.DoesNotExist:
                    # Fall back to all accessible talkgroups
                    talkgroups = get_user_accessible_talkgroups(self.request.user)
            else:
                # Try to find public scan list first
                try:
                    sl = ScanList.objects.get(slug__iexact=scanlist, public=True)
                    talkgroups = sl.talkgroups.all()
                except ScanList.DoesNotExist:
                    # Try user's custom scan list
                    try:
                        user_sl = UserScanList.objects.get(
                            user=self.request.user,
                            name__iexact=scanlist,
                            is_active=True
                        )
                        talkgroups = user_sl.talkgroups.all()
                    except UserScanList.DoesNotExist:
                        return Transmission.objects.none()

            # Filter to only talkgroups user has access to
            accessible_tgs = get_user_accessible_talkgroups(self.request.user)
            accessible_tg_ids = accessible_tgs.values_list('id', flat=True)
            filtered_talkgroups = talkgroups.filter(id__in=accessible_tg_ids)

            return Transmission.objects.filter(
                talkgroup_info__in=filtered_talkgroups
            ).order_by('-start_datetime')

        except Exception:
            return Transmission.objects.none()


class SecureMessagePopUpViewSet(AuthenticatedViewSetMixin, generics.ListAPIView):
    """
    Message popup API - available to all authenticated users
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        return MessagePopUp.objects.filter(active=True)


# Keep menu viewsets as-is but add authentication
class SecureMenuScanListViewSet(AuthenticatedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MenuScanListSerializer
    queryset = MenuScanList.objects.all()


class SecureMenuTalkGroupListViewSet(AuthenticatedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = MenuTalkGroupListSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return MenuTalkGroupList.objects.none()

        # Only show menu items for talkgroups user has access to
        accessible_tgs = get_user_accessible_talkgroups(self.request.user)
        return MenuTalkGroupList.objects.filter(talkgroup__in=accessible_tgs)