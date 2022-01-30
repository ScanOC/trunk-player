#import functools
import ssl
import sys
import re
import json
import pytz
from itertools import chain
from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic import ListView
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from .models import *
from rest_framework import viewsets, generics
from .serializers import TransmissionSerializer, TalkGroupSerializer, ScanListSerializer, MenuScanListSerializer, MenuTalkGroupListSerializer, MessageSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins



from allauth.account.models import EmailAddress as allauth_emailaddress
from pprint import pprint
from django.contrib import messages
import logging

from .forms import *

logger = logging.getLogger(__name__)


def check_anonymous(decorator):
    """
    Decarator used to see if we allow anonymous access
    """
    anonymous = getattr(settings, 'ALLOW_ANONYMOUS', True)
    return decorator if not anonymous else lambda x: x


@login_required
def userScanList(request):
    template = 'radio/userscanlist.html'
    if request.method == "POST":
        form = UserScanForm(request.POST)
        if form.is_valid():
            print('Form Valid')
            name = form.cleaned_data['name']
            tgs = form.cleaned_data['talkgroups']
            print('Form Data [{}] [{}]'.format(name, tgs))
            sl = ScanList()
            sl.created_by = request.user
            sl.name = name
            sl.description = name
            sl.save()
            sl.talkgroups.add(*tgs)
            return redirect('user_profile')
        else:
            print('Form not Valid')
    else:
        form = UserScanForm()
    return render(request, template, {'form': form})

@login_required
def userProfile(request):
    template = 'radio/profile.html'
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        profile_form = UserForm(instance=request.user)
        profile = Profile.objects.get(user=request.user)
        scan_lists = ScanList.objects.filter(created_by=request.user)
        return render(request, template, {'profile_form': profile_form, 'profile': profile, 'scan_lists': scan_lists} )

def agencyList(request):
    template = 'radio/agency_list.html'
    query_data = Agency.objects.exclude(short='_DEF_').order_by('name')

    return render(request, template, {'agency': query_data})


def cityListView(request):
    template = 'radio/city_list.html'
    query_data = City.objects.filter(visible=True)

    return render(request, template, {'cities': query_data})


def cityDetailView(request, slug):
    template = 'radio/city_detail.html'
    query_data = City.objects.get(slug=slug)

    return render(request, template, {'object': query_data})
    

def TransDetailView(request, slug):
    template = 'radio/transmission_detail.html'
    status = 'Good'
    try:
        query_data = Transmission.objects.filter(slug=slug)
        if not query_data:
            raise Http404
    except Transmission.DoesNotExist:
        raise Http404
    query_data2 = limit_transmission_history(request, query_data)
    if not query_data2 and not query_data[0].incident_set.filter(public=True):
        query_data[0].audio_file = None
        status = 'Expired'
    restricted, new_query = restrict_talkgroups(request, query_data)
    if not new_query:
        raise Http404
    return render(request, template, {'object': query_data[0], 'status': status})

def transDownloadView(request, slug):
    import requests
    try:
        query_data = Transmission.objects.filter(slug=slug)
        if not query_data:
            raise Http404
    except Transmission.DoesNotExist:
        raise Http404

    query_data2 = limit_transmission_history(request, query_data)
    if not query_data2: raise Http404  # Just raise 404 if its too old

    restricted, new_query = restrict_talkgroups(request, query_data)
    if not new_query: raise Http404

    trans = new_query[0]
    if trans.audio_file_type == 'm4a':
        audio_type = 'audio/m4a'
    else:
        audio_type = 'audio/mp3'

    response = HttpResponse(content_type=audio_type)
    start_time = timezone.localtime(trans.start_datetime).strftime('%Y%m%d_%H%M%S')

    filename = '{}_{}.{}'.format(start_time, trans.talkgroup_info.slug, trans.audio_file_type)

    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    url = 'https:{}{}.{}'.format(trans.audio_url, trans.audio_file, trans.audio_file_type)
    if trans.audio_url[:2] != '//':
        url = 'http:'
        if request.is_secure():
            url = 'https:'
        url += '//{}/{}{}.{}'.format(request.get_host(), trans.audio_url, trans.audio_file, trans.audio_file_type)

    data = requests.get(url, verify=False)
    response.write(data.content)

    return response


class TransmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Transmission.objects.none()
    serializer_class = TransmissionSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class ScanListViewSet(viewsets.ModelViewSet):
    queryset = ScanList.objects.all().prefetch_related('talkgroups')
    serializer_class = ScanListSerializer


class TalkGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
#    queryset = TalkGroup.objects.filter(public=True)
    serializer_class = TalkGroupSerializer
    base_name = 'TalkGroup'

    def get_queryset(self):
        if settings.ACCESS_TG_RESTRICT:
            tg = allowed_tg_list(self.request.user)
        else:
            tg = TalkGroup.objects.filter(public=True)
        return tg



class TransmissionView(ListView):
    model = Transmission
    paginate_by = 50


def ScanListFilter(request, filter_val):
    template = 'radio/transmission.html'
    return render(request, template, {'filter_data': filter_val, 'api_url': '/api_v1/ScanList'})


def TalkGroupFilterNew(request, filter_val):
    template = 'radio/transmission_play.html'
    return render(request, template, {'filter_data': filter_val})


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

def get_user_profile(user):
    if user.is_authenticated:
        user_profile = Profile.objects.get(user=user)
    else:
        try:
            anon_user = User.objects.get(username='ANONYMOUS_USER')
        except User.DoesNotExist:
            raise ImproperlyConfigured('ANONYMOUS_USER is missing from User table, was "./manage.py migrations" not run?')
        user_profile = Profile.objects.get(user=anon_user)
    return user_profile

def get_history_allow(user):
    user_profile = get_user_profile(user)
    if user_profile:
        history_minutes = user_profile.plan.history
    else:
        history_minutes = settings.ANONYMOUS_TIME
    return history_minutes


def limit_transmission_history(request, query_data):
    history_minutes = get_history_allow(request.user)
    if history_minutes > 0:
        time_threshold = timezone.now() - timedelta(minutes=history_minutes)
        query_data = query_data.filter(start_datetime__gt=time_threshold)
    return query_data

def limit_transmission_history_six_months(request, query_data):
    history_minutes = 259200
    time_threshold = timezone.now() - timedelta(minutes=history_minutes)
    query_data = query_data.filter(start_datetime__gt=time_threshold)
    return query_data



def allowed_tg_list(user):
    user_profile = get_user_profile(user)
    tg_list = None
    for group in user_profile.talkgroup_access.all():
       if tg_list is None:
           tg_list = group.talkgroups.all()
       else:
           tg_list = tg_list | group.talkgroups.all()
    if tg_list:
        tg_list = tg_list.distinct()
    else:
        # Set blank talkgroup queryset
        tg_list = TalkGroup.objects.none()
    return tg_list


def restrict_talkgroups(request, query_data):
    ''' Checks to make sure the user can view
        each of the talkgroups in the query_data
        returns ( was_restricted, new query_data )
    '''
    if not settings.ACCESS_TG_RESTRICT:
        return False, query_data
    tg_list = allowed_tg_list(request.user)
    query_data = query_data.filter(talkgroup_info__in=tg_list)
    return None, query_data
    

def TalkGroupFilterBase(request, filter_val, template):
    try:
        tg = TalkGroup.objects.get(alpha_tag__startswith=filter_val)
    except TalkGroup.DoesNotExist:
        raise Http404
    try:
        query_data = Transmission.objects.filter(talkgroup_info=tg).prefetch_related('units')
        #query_data = limit_transmission_history(self.request, rc_data)
        query_data = limit_transmission_history_six_months(self.request, rc_data)
        restrict_talkgroups(self.request, rc_data)
    except Transmission.DoesNotExist:
        raise Http404
    return render(request, template, {'object_list': query_data, 'filter_data': filter_val})


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
        rc_data = Transmission.objects.filter(talkgroup_info__in=tg).prefetch_related('units').prefetch_related('talkgroup_info')
        #rc_data = limit_transmission_history(self.request, rc_data)
        rc_data = limit_transmission_history_six_months(self.request, rc_data)
        restricted, rc_data = restrict_talkgroups(self.request, rc_data) 
        return rc_data


class IncViewSet(generics.ListAPIView):
    serializer_class = TransmissionSerializer

    def get_queryset(self):
        inc = self.kwargs['filter_val']
        try:
            if self.request.user.is_staff:
                rc_data = Incident.objects.get(slug__iexact=inc).transmissions.all()
            else:
                rc_data = Incident.objects.get(slug__iexact=inc, public=True).transmissions.all()
        except Incident.DoesNotExist:
               print("Incident does not exist")
               raise
        restricted, rc_data = restrict_talkgroups(self.request, rc_data)
        return rc_data


class MessagePopUpViewSet(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return MessagePopUp.objects.filter(active=True)


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
        #rc_data = limit_transmission_history(self.request, rc_data)
        rc_data = limit_transmission_history_six_months(self.request, rc_data)
        restricted, rc_data = restrict_talkgroups(self.request, rc_data)
        return rc_data


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
        #rc_data = limit_transmission_history(self.request, rc_data)
        rc_data = limit_transmission_history_six_months(self.request, rc_data)
        restricted, rc_data = restrict_talkgroups(self.request, rc_data)
        return rc_data


class TalkGroupList(ListView):
    model = TalkGroup
    context_object_name = 'talkgroups'
    template_name = 'radio/talkgroup_list.html'

    #queryset = TalkGroup.objects.filter(public=True)
    def get_queryset(self):
        if settings.ACCESS_TG_RESTRICT:
            tg = allowed_tg_list(self.request.user)
        else:
            tg = TalkGroup.objects.filter(public=True)
        if self.request.GET.get('recent', None):
            tg = tg.order_by('-recent_usage', '-last_transmission')
        return tg



@login_required
@csrf_protect
def upgrade(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                'registration/upgrade.html',
                {'form': form},
            )

        try:
            plan = form.cleaned_data.get('plan_type')
            card_name = form.cleaned_data.get('cardholder_name')
            stripe_cust = None
            logger.error('Change plan to {} for customer {} Card Name {}'.format(plan, stripe_cust, card_name))
            stripe_info = None
        except stripe.InvalidRequestError as e:
            messages.error(request, "Error with stripe {}".format(e))
            logger.error("Error with stripe {}".format(e))
            return render(
                request,
                'registration/upgrade.html',
                {'form': form},
            )
        except stripe.CardError as e:
            messages.error(request, "<b>Error</b> Sorry there was an error with processing your card:<br>{}".format(e))
            logger.error("Error with stripe user card{}".format(e))
            return render(
                request,
                'registration/upgrade.html',
                {'form': form},
            )

        print('------ STRIPE DEBUG -----')
        pprint(stripe_info, sys.stderr)
        return render(
           request,
           'registration/upgrade_complete.html',
        )
    else:
        form = PaymentForm()
        return render(
           request,
           'registration/upgrade.html',
           {'form': form, },
        )


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
                    #stripe_actions.customers.create(user=new_user)
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

    def form_valid(self, form):
        try:
            update_unit_email = SiteOption.objects.get(name='SEND_ADMIN_EMAIL_ON_UNIT_NAME')
            if update_unit_email.value_boolean_or_string() == True:
                Unit = form.save()
                send_mail(
                  'Unit ID Change',
                  'User {} updated unit ID {} Now {}'.format(self.request.user, Unit.dec_id, Unit.description),
                  settings.SERVER_EMAIL,
                  [ mail for name, mail in settings.ADMINS],
                  fail_silently=False,
                )
        except SiteOption.DoesNotExist:
            pass
        return super().form_valid(form)


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
    return render(request, template, {'object_list': query_data, 'scanlist': scanlist, 'request': request})


@login_required
@csrf_protect
def cancel_plan(request):
    template = 'radio/cancel.html'
    if request.method == 'POST':
        msg = 'User {} ({}) wants to cancel'.format(request.user.username, request.user.pk)
        mail_admins('Cancel Subscription', msg )
        return render(request, template, {'complete': True})
    else:
        return render(request, template, {'complete': False})

@csrf_protect
def plans(request):
    token = None
    has_verified_email = False
    plans = None
    default_plan = None
    if request.method == 'POST':
        template = 'radio/subscribed.html'
        token = request.POST.get('stripeToken')
        plan = request.POST.get('plan')
        # See if this user already has a stripe account
        try:
            stripe_cust = None
        except ObjectDoesNotExist:
            #stripe_actions.customers.create(user=request.user)
            stripe_cust = None
        try:
            stripe_info = None #stripe_actions.subscriptions.create(customer=stripe_cust, plan=plan, token=request.POST.get('stripeToken'))
        except Exception as e: #stripe.CardError as e:
            template = 'radio/charge_failed.html'
            logger.error("Error with stripe user card{}".format(e))
            return render(request, template, {'error_msg': e })

        for t in request.POST:
          logger.error("{} {}".format(t, request.POST[t]))
    else:
        template = 'radio/plans.html'
        plans = StripePlanMatrix.objects.filter(order__lt=99).filter(active=True)
        default_plan = Plan.objects.get(pk=Plan.DEFAULT_PK)

        # Check if users email address is verified
        if request.user.is_authenticated:
            verified_email = allauth_emailaddress.objects.filter(user=request.user, primary=True, verified=True)
            if verified_email:
                has_verified_email = True


    return render(request, template, {'token': token, 'verified_email': has_verified_email, 'plans': plans, 'default_plan': default_plan} )

def incident(request, inc_slug):
    template = 'radio/player_main.html'
    try:
        if request.user.is_staff:
            inc = Incident.objects.get(slug=inc_slug)
        else:
            inc = Incident.objects.get(slug=inc_slug, public=True)
    except Incident.DoesNotExist:
        raise Http404
    return render(request, template, {'inc':inc})


@csrf_exempt
def import_transmission(request):
    if request.method == "POST":
        settings_auth_token = getattr(settings, 'ADD_TRANS_AUTH_TOKEN', None)
        if settings_auth_token == '7cf5857c61284': # Check is default is still set
            return HttpResponse('Unauthorized, default ADD_TRANS_AUTH_TOKEN still set.', status=401)
        body_unicode = request.body.decode('utf-8')
        request_data = json.loads(body_unicode)
        auth_token = request_data.get('auth_token')
        if auth_token != settings_auth_token:
            return HttpResponse('Unauthorized, check auth_token', status=401)
        # System
        system_name = request_data.get('system')
        if system_name is None:
            return HttpResponse('system is missing', status=400)
        system, created = System.objects.get_or_create(name=system_name)
        # Source
        source_name = request_data.get('source')
        if source_name is None:
            return HttpResponse('source is missing', status=400)
        source, created = Source.objects.get_or_create(description=source_name)
        # TalkGroup
        tg_dec = request_data.get('talkgroup')
        if tg_dec is None:
            return HttpResponse('talkgroup is missing', status=400)
        try:
            tg = TalkGroup.objects.get(dec_id=tg_dec, system=system)
        except TalkGroup.DoesNotExist:
            name = '#{}'.format(tg_dec)
            tg = TalkGroup.objects.create(dec_id=tg_dec, system=system, alpha_tag=name, description='TalkGroup {}'.format(name))
        # Transmission start
        epoc_ts = request_data.get('start_time')
        start_dt = datetime.fromtimestamp(int(epoc_ts), pytz.UTC)
        epoc_end_ts = request_data.get('stop_time')
        end_dt = datetime.fromtimestamp(int(epoc_end_ts), pytz.UTC)
        play_length = epoc_end_ts - epoc_ts
        audio_filename = request_data.get('audio_filename')
        audio_file_url_path = request_data.get('audio_file_url_path')
        freq = request_data.get('freq') # This should be depricated
        audio_file_type = request_data.get('audio_file_type')
        audio_file_play_length = request_data.get('audio_file_play_length', play_length)
        has_audio = request_data.get('has_audio', True)

        t = Transmission( start_datetime = start_dt,
                     end_datetime = end_dt,
                     audio_file = audio_filename,
                     talkgroup = tg_dec,
                     talkgroup_info = tg,
                     freq = int(float(freq)),
                     emergency = False,
                     source = source,
                     system = system,
                     audio_file_url_path = audio_file_url_path,
                     audio_file_type = audio_file_type,
                     play_length = audio_file_play_length,
                     has_audio = has_audio,
                   )
        t.save()

        # Units
        count = 0
        for unit in request_data.get('srcList'):
                try:
                    trans_unit = unit['src']
                except TypeError:
                    trans_unit = unit
                u,created = Unit.objects.get_or_create(dec_id=trans_unit,system=t.system)
                tu = TranmissionUnit.objects.create(transmission=t, unit=u, order=count)
                count=count+1

        return HttpResponse("Transmission added [{}]".format(t.pk))
    else:
        return HttpResponse(status=405)
