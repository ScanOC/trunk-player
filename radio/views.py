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
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import *
from rest_framework import viewsets, generics
from .serializers import TransmissionSerializer, TalkGroupSerializer, ScanListSerializer, MenuScanListSerializer, MenuTalkGroupListSerializer
from datetime import datetime, timedelta
from .forms import *

class TransDetailView(DetailView):
    model = Transmission

class TransmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer

class ScanListViewSet(viewsets.ModelViewSet):
    queryset = ScanList.objects.all()
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

def TalkGroupFilterBase(request, filter_val, template):
    try:
        tg = TalkGroup.objects.get(alpha_tag__startswith=filter_val)
    except TalkGroup.DoesNotExist:
        raise Http404
    try:
        query_data = Transmission.objects.filter(talkgroup_info=tg)
        if not request.user.is_authenticated() and settings.ANONYMOUS_TIME != 0:
            time_threshold = datetime.now() - timedelta(minutes=settings.ANONYMOUS_TIME)
            query_data = query_data.filter(start_datetime__gt=time_threshold)

    except Transmission.DoesNotExist:
        raise Http404
    return render_to_response(template, {'object_list': query_data, 'filter_data': filter_val})

class ScanViewSet(generics.ListAPIView):
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        scanlist = self.kwargs['filter_val']
        try:
            sl = ScanList.objects.get(name=scanlist)
        except ScanList.DoesNotExist:
            if scanlist == 'default':
                tg = TalkGroup.objects.all()
            else:
               print("Scan list does not match")
               raise
        else:
            tg = sl.talkgroups.all()
        rc_data = Transmission.objects.filter(talkgroup_info__in=tg)
        if not self.request.user.is_authenticated() and settings.ANONYMOUS_TIME != 0:
            time_threshold = datetime.now() - timedelta(minutes=settings.ANONYMOUS_TIME)
            rc_data = rc_data.filter(start_datetime__gt=time_threshold)
        return rc_data

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
        rc_data = Transmission.objects.filter(talkgroup_info__in=tg)
        if not self.request.user.is_authenticated() and settings.ANONYMOUS_TIME != 0:
            time_threshold = datetime.now() - timedelta(minutes=settings.ANONYMOUS_TIME)
            rc_data = rc_data.filter(start_datetime__gt=time_threshold)
        return rc_data

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
