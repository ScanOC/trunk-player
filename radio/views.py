#import functools
import re
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import Http404
from django.views.generic import ListView
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from .models import *
from rest_framework import viewsets, generics
from .serializers import TransmissionSerializer, TalkGroupSerializer, ScanListSerializer, MenuScanListSerializer, MenuTalkGroupListSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import *

def check_anonymous(decorator):
    """
    Decarator used to see if we allow anonymous access
    """
    anonymous = getattr(settings, 'ALLOW_ANONYMOUS', True)
    return decorator if not anonymous else lambda x: x


class TransDetailView(DetailView):
    model = Transmission


class TransmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Transmission.objects.all().prefetch_related('units')
    serializer_class = TransmissionSerializer


class ScanListViewSet(viewsets.ModelViewSet):
    queryset = ScanList.objects.all().prefetch_related('talkgroups')
    serializer_class = ScanListSerializer


class TalkGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = TalkGroup.objects.filter(public=True)
    serializer_class = TalkGroupSerializer


class TransmissionView(ListView):
    model = Transmission
    paginate_by = 50


def ScanListFilter(request, filter_val):
    template = 'radio/transmission.html'
    return render_to_response(template, {'filter_data': filter_val, 'api_url': '/api_v1/ScanList'})


def TalkGroupFilterNew(request, filter_val):
    template = 'radio/transmission_play.html'
    return render_to_response(template, {'filter_data': filter_val})


def TalkGroupFilterjq(request, filter_val):
    template = 'radio/transmission_list_jq.html'
    return TalkGroupFilterBase(request, filter_val, template)


def TalkGroupFilter(request, filter_val):
    template = 'radio/transmission_list.html'
    return TalkGroupFilterBase(request, filter_val, template)

# Open to anyone
def Generic(request, page_name):
    template = 'radio/generic.html'
    query_data = WebHtml.objects.get(name=page_name)
    return render(request, template, {'html_object': query_data})

def limit_transmission_history(request, query_data):
    if request.user.is_authenticated():
        user_profile = Profile.objects.get(user=request.user)
    else:
        try:
            anon_user = User.objects.get(username='ANONYMOUS_USER')
        except User.DoesNotExist:
            raise ImproperlyConfigured('ANONYMOUS_USER is missing from User table, was "./manage.py migrations" not run?')
        user_profile = Profile.objects.get(user=anon_user)
    if user_profile:
        history_minutes = user_profile.plan.history
    else:
        history_minutes = settings.ANONYMOUS_TIME
    if history_minutes > 0:
        time_threshold = timezone.now() - timedelta(minutes=history_minutes)
        query_data = query_data.filter(start_datetime__gt=time_threshold)
    return query_data


def TalkGroupFilterBase(request, filter_val, template):
    try:
        tg = TalkGroup.objects.get(alpha_tag__startswith=filter_val)
    except TalkGroup.DoesNotExist:
        raise Http404
    try:
        query_data = Transmission.objects.filter(talkgroup_info=tg).prefetch_related('units')
        query_data = limit_transmission_history(self.request, rc_data)
    except Transmission.DoesNotExist:
        raise Http404
    return render_to_response(template, {'object_list': query_data, 'filter_data': filter_val})


class ScanViewSet(generics.ListAPIView):
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        scanlist = self.kwargs['filter_val']
        try:
            sl = ScanList.objects.get(slug__iexact=scanlist)
        except ScanList.DoesNotExist:
            if scanlist == 'default':
                tg = TalkGroup.objects.all()
            else:
               print("Scan list does not match")
               raise
        else:
            tg = sl.talkgroups.all()
        rc_data = Transmission.objects.filter(talkgroup_info__in=tg).prefetch_related('units')
        return limit_transmission_history(self.request, rc_data)


class TalkGroupFilterViewSet(generics.ListAPIView):
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        tg_var = self.kwargs['filter_val']
        search_tgs = re.split('[\+]', tg_var)
        q = Q()
        for stg in search_tgs:
            q |= Q(common_name__iexact=stg)
            q |= Q(slug__iexact=stg)
        tg = TalkGroup.objects.filter(q)
        rc_data = Transmission.objects.filter(talkgroup_info__in=tg).prefetch_related('units')
        return limit_transmission_history(self.request, rc_data)


class UnitFilterViewSet(generics.ListAPIView):
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        unit_var = self.kwargs['filter_val']
        search_unit = re.split('[\+]', unit_var)
        q = Q()
        for s_unit in search_unit:
            q |= Q(slug__iexact=s_unit)
        units = Unit.objects.filter(q)
        rc_data = Transmission.objects.filter(units__in=units).filter(talkgroup_info__public=True).prefetch_related('units').distinct()
        return limit_transmission_history(self.request, rc_data)


class TalkGroupList(ListView):
    model = TalkGroup
    context_object_name = 'talkgroups'

    queryset = TalkGroup.objects.filter(public=True)


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                if new_user.is_active:
                    login(request, new_user)
                    return HttpResponseRedirect('/scan/default/')
                else:
                    # this would be weird to get here
                    return HttpResponseRedirect('/register/success/')
            else:
                return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
 
    return render(
    request,
    'registration/register.html',
    { 'form': form },
    )

def register_success(request):
    return render(
    request,
    'registration/success.html', {},
    )


class MenuScanListViewSet(viewsets.ModelViewSet):
    serializer_class = MenuScanListSerializer
    queryset = MenuScanList.objects.all()


class MenuTalkGroupListViewSet(viewsets.ModelViewSet):
    serializer_class = MenuTalkGroupListSerializer
    queryset = MenuTalkGroupList.objects.all()


class UnitUpdateView(PermissionRequiredMixin, UpdateView):
    model = Unit
    form_class = UnitEditForm
    success_url = '/unitupdategood/'
    permission_required = ('radio.change_unit')


def ScanDetailsList(request, name):
    template = 'radio/scandetaillist.html'
    scanlist = None
    try:
        scanlist = ScanList.objects.get(name=name)
    except ScanList.DoesNotExist:
        if name == 'default':
            query_data = TalkGroup.objects.all()
        else:
            raise Http404
    if scanlist:
        query_data = scanlist.talkgroups.all()
    return render_to_response(template, {'object_list': query_data, 'scanlist': scanlist, 'request': request})

