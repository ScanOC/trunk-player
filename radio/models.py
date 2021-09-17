import json
import logging
import uuid
import urllib.parse

from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.utils import OperationalError

import radio.choices as choice

log = logging.getLogger(__name__)

class Agency(models.Model):
    name = models.CharField(max_length=100)
    short = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name

    def get_short(self):
        return self.short


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    url = models.URLField(max_length=400, null=True, blank=True)
    google_maps_url = models.URLField(max_length=400, null=True, blank=True)
    fire_service = models.ForeignKey(Agency, related_name='fire_service', null=True, blank=True, on_delete=models.CASCADE)
    police_service = models.ForeignKey(Agency, related_name='police_service', null=True, blank=True, on_delete=models.CASCADE)
    ems_service = models.ForeignKey(Agency, related_name='ems_service', null=True, blank=True, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)


class System(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True)
    system_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    description = models.CharField(max_length=100, db_index=True, unique=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.description

class Unit(models.Model):
    dec_id = models.IntegerField()
    description = models.CharField(max_length=100, blank=True, null=True)
    agency = models.ForeignKey(Agency, default=settings.RADIO_DEFAULT_UNIT_AGENCY, on_delete=models.CASCADE)
    #agency = models.ForeignKey(Agency, default=2)
    type = models.CharField(max_length=1, choices=choice.RADIO_TYPE_CHOICES, default=choice.RADIO_TYPE_MOBILE)
    number = models.IntegerField(default=1)
    system = models.ForeignKey(System, default=0, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True)

    class Meta:
        unique_together = ('dec_id', 'system',)

    def __str__(self):
        if(self.description):
            return self.description
        else:
            return str(self.dec_id)

    def save(self, *args, **kwargs):
        if self.description:
            self.slug = slugify(self.description)
        else:
            self.slug = slugify(self.dec_id)
        super(Unit, self).save(*args, **kwargs)


class RepeaterSite(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class TalkGroup(models.Model):
    dec_id = models.IntegerField()
    alpha_tag = models.CharField(max_length=30)
    common_name = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(null=True)
    public = models.BooleanField(default=True)
    comments = models.CharField(max_length=100, blank=True, null=True)
    system = models.ForeignKey(System, default=0, on_delete=models.CASCADE)
    mode = models.CharField(max_length=1, choices=choice.TG_MODE_CHOICES, default=choice.TG_MODE_DIGITAL, help_text='mode used by trunk-recorder')
    priority = models.IntegerField(default=3, help_text='record priority used by trunk-recorder')
    _home_site = models.ForeignKey(RepeaterSite, blank=True, null=True, on_delete=models.CASCADE)
    _service_type = models.ForeignKey(Service, blank=True, null=True, on_delete=models.CASCADE)
    last_transmission = models.DateTimeField()
    recent_usage = models.IntegerField(default=0)
    play_source = models.ForeignKey(Source, blank=True, null=True, help_text='default record source for playback', on_delete=models.CASCADE)

    class Meta:
        ordering = ["alpha_tag"]
        unique_together = ('dec_id', 'system',)

    def __str__(self):
        return self.alpha_tag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.alpha_tag)
        if not self.last_transmission:
            self.last_transmission = timezone.now()
        super(TalkGroup, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/tg/{}/'.format(self.slug)

    @property
    def home_site(self):
        return self._home_site

    @home_site.setter
    def home_site(self, value):
        hs, created = RepeaterSite.objects.get_or_create(name=value)
        self._home_site = hs

    @property
    def service_type(self):
        return self._service_type

    @service_type.setter
    def service_type(self, value):
        st, created = Service.objects.get_or_create(name=value)
        self._service_type = st


def AddToDefaultAccessGroup(sender, instance, created, **kwargs):
    if created:
        new_tg = TalkGroupWithSystem.objects.get(pk=instance.pk)
        for access_group in TalkGroupAccess.objects.filter(default_new_talkgroups=True):
            access_group.talkgroups.add(new_tg)
            access_group.save()


post_save.connect(AddToDefaultAccessGroup, sender=TalkGroup)


class TalkGroupWithSystem(TalkGroup):
    class Meta:
        proxy = True

    def __str__(self):
        return "{} ({})".format(self.alpha_tag, self.system)


class Transmission(models.Model):
    slug = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False) 
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    audio_file = models.FileField()
    audio_file_type = models.CharField(max_length=3, null=True, default='mp3')
    audio_file_url_path = models.CharField(max_length=100, default='/')
    talkgroup = models.IntegerField()
    talkgroup_info = models.ForeignKey(TalkGroup, on_delete=models.CASCADE)
    freq = models.IntegerField()
    emergency = models.BooleanField(default=False)
    units = models.ManyToManyField(Unit, through='TranmissionUnit')
    play_length = models.FloatField(default=0.0)
    source = models.ForeignKey(Source, default=0, on_delete=models.CASCADE)
    system = models.ForeignKey(System, default=0, on_delete=models.CASCADE)
    from_default_source = models.BooleanField(default=True)
    has_audio = models.BooleanField(default=True)

    def __str__(self):
        return '{} {}'.format(self.talkgroup, self.start_datetime)

    def get_absolute_url(self):
        return '/audio/{}/'.format(self.slug)

    @property
    def local_start_datetime(self):
        return timezone.localtime(self.start_datetime).strftime(settings.TRANS_DATETIME_FORMAT)

    def as_dict(self):
        return {'start_datetime': str(self.start_datetime), 
                #'audio_file': str(self.audio_file), 
                #'talkgroup_desc': str(self.talkgroup_info.alpha_tag),
                'talkgroup_slug': self.talkgroup_info.slug,
                'talkgroup_dec_id' : str(self.talkgroup_info.dec_id),
                #'audio_url': str("{}{}.{}".format(settings.AUDIO_URL_BASE, self.audio_file, self.audio_file_type))
               }


    def print_play_length(self):
        m, s = divmod(int(self.play_length), 60)
        return '{:02d}:{:02d}'.format(m,s)

    def freq_mhz(self):
        return '{0:07.3f}'.format(self.freq / 1000000)

    def tg_name(self):
        """Returns TalkGroup name used for page title
           First tries TalkGroup.common_name
           then TalkGroup.alpha_tag
        """
        if self.talkgroup_info.common_name:
            return self.talkgroup_info.common_name
        else:
            return self.talkgroup_info.alpha_tag

    def is_playable(self, user):
        """If the user can play this transmission
        """
        return True

    def _get_user_profile(self, user):
        if user.is_authenticated:
            user_profile = Profile.objects.get(user=user)
        else:
            try:
                anon_user = User.objects.get(username='ANONYMOUS_USER')
            except User.DoesNotExist:
                raise ImproperlyConfigured('ANONYMOUS_USER is missing from User table, was "./manage.py migrations" not run?')
            user_profile = Profile.objects.get(user=anon_user)
        return user_profile



    def _get_history_allow(self,user):
        user_profile = self._get_user_profile(user)
        if user_profile:
            history_minutes = user_profile.plan.history
        else:
            history_minutes = settings.ANONYMOUS_TIME
        return history_minutes


    def audio_file_history_check(self, user):
        history_minutes = self._get_history_allow(user)
        if history_minutes > 0:
            time_threshold = timezone.now() - timedelta(minutes=history_minutes)
            if self.start_datetime < time_threshold:
                return None
        return str(self.audio_file)

    @property
    def audio_url(self):
        base_path = settings.AUDIO_URL_BASE
        return urllib.parse.urljoin(base_path, self.audio_file_url_path.lstrip('/'))

    class Meta:
        ordering = ["-pk"]
        permissions = (
            ('download_audio', 'Can download audio clips'),
        )

    def save(self, *args, **kwargs):
        if settings.FIX_AUDIO_NAME:
            file_name = str(self.audio_file)
            self.audio_file = file_name.replace('+', '%2B')
        if self.talkgroup_info.play_source is not None and \
               self.talkgroup_info.play_source != self.source:
           self.from_default_source = False
        else:
           self.from_default_source = True
        super(Transmission, self).save(*args, **kwargs)


@receiver(post_save, sender=Transmission, dispatch_uid="send_mesg")
def send_mesg(sender, instance, **kwargs):
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    #log.debug('Hit post save()')
    #log.debug('DATA %s', json.dumps(instance.as_dict()))
    #log.error('DATA %s', json.dumps(instance.as_dict()))
    tg = TalkGroup.objects.get(pk=instance.talkgroup_info.pk)
    tg.last_transmission = timezone.now()
    tg.save()
    groups = tg.scanlist_set.all()

    payload = instance.as_dict()
    payload["scan-groups"] = [g.slug for g in groups]
    # for g in groups:        
    #     async_to_sync(channel_layer.group_send)(
    #     'livecall-scan-'+g.slug, {
    #         'type':'radio_message',
    #         'text': json.dumps(payload)
    #     })


    # async_to_sync(channel_layer.group_send)(
    #     'livecall-tg-' + tg.slug, {
    #         'type':'radio_message',
    #         'text': json.dumps(payload)
    #     })

    
    # Send notification to default group all the time
    async_to_sync(channel_layer.group_send)(
        'livecall-scan-default', {
            'type':'radio_message',
            'text': json.dumps(payload)
        })


    #def save(self, *args, **kwargs):
    #    try:
    #        self.talkgroup_info = TalkGroup.objects.get(dec_id=self.talkgroup)
    #    except TalkGroup.DoesNotExist:
    #        new_tg = TalkGroup(dec_id=self.talkgroup, alpha_tag='UNK')
    #        new_tg.save
    #        self.talkgroup_info = TalkGroup.objects.get(dec_id=self.talkgroup)
    #    super(Transmission, self).save(*args, **kwargs)

class TranmissionUnit(models.Model):
    transmission = models.ForeignKey(Transmission, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return '{} on {}'.format(self.unit,self.transmission)

class ScanList(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    talkgroups = models.ManyToManyField(TalkGroup)
    slug = models.SlugField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ScanList, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/scan/{}/'.format(self.slug)

class MenuList(models.Model):
    order = models.IntegerField(default=1)

    class Meta:
        abstract = True
        ordering = ["order", "name"]

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def scan_name(self):
        return self.name

    @property
    def scan_description(self):
        return self.name.description

    @property
    def scan_slug(self):
        return self.name.slug

class MenuScanList(MenuList):
    name = models.ForeignKey(ScanList, on_delete=models.CASCADE)

    @property
    def scan_name(self):
        return self.name.name

    @property
    def scan_description(self):
        return self.name.description


class MenuTalkGroupList(MenuList):
    name = models.ForeignKey(TalkGroupWithSystem, on_delete=models.CASCADE)

    @property
    def tg_name(self):
        return self.name.alpha_tag

    @property
    def tg_slug(self):
        return self.name.slug

class TalkGroupAccess(models.Model):
    name = models.CharField(max_length=30, unique=True)
    talkgroups = models.ManyToManyField(TalkGroupWithSystem)
    default_group = models.BooleanField(default=False, help_text='new users get this group by default')
    default_new_talkgroups = models.BooleanField(default=False, help_text='new talkgroups are added to this group')
    

    class Meta:
        verbose_name_plural = 'talk group access'

    def __str__(self):
        return '{}'.format(self.name)


class Plan(models.Model):
    DEFAULT_PK = 1 # This is added via a migration
    name = models.CharField(max_length=30, unique=True)
    history = models.IntegerField(default=15, help_text='visible history in minutes')

    def __str__(self):
        return '{}'.format(self.name)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, default=Plan.DEFAULT_PK, on_delete=models.CASCADE)
    talkgroup_access = models.ManyToManyField(TalkGroupAccess, blank=True)


class WebHtml(models.Model):
    name = models.CharField(max_length=30, unique=True)
    bodytext = models.TextField()
    
    def __str__(self):
        return self.name


class StripePlanMatrix(models.Model):
    name = models.CharField(max_length=30, unique=True)
    radio_plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=99)

    class Meta:
        ordering = ["order"]


    def __str__(self):
       return self.name


    def stripe_amount(self):
       return int(self.stripe_plan.amount * 100)

    def history_days(self):
       return int(self.radio_plan.history / 1440)


class SiteOption(models.Model):
    name = models.CharField(max_length=30, unique=True)
    value = models.CharField(max_length=60)
    javascript_visible = models.BooleanField(default=False)
    template_visible = models.BooleanField(default=False)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def value_boolean_or_string(self):
        if self.value.lower() == 'true':
            return True
        elif self.value.lower() == 'false':
            return False
        else:
            return self.value


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        default_plan = Plan.objects.get(pk=Plan.DEFAULT_PK)
        up = Profile(user=user, plan=default_plan)
        up.save()
        try:
            for tg in TalkGroupAccess.objects.filter(default_group=True):
                up.talkgroup_access.add(tg)
        except OperationalError:
            pass
        try:
            new_user_email = SiteOption.objects.get(name='SEND_ADMIN_EMAIL_ON_NEW_USER')
            if new_user_email.value_boolean_or_string() == True:
                send_mail(
                      'New {} User {}'.format(settings.SITE_TITLE, user.username),
                      'New User {} {} Username {} Email {} just registered'.format(user.first_name, user.last_name, user.username, user.email),
                      settings.SERVER_EMAIL,
                      [ mail for name, mail in settings.ADMINS],
                      fail_silently=False,
                     )
        except (SiteOption.DoesNotExist, OperationalError):
            pass

post_save.connect(create_profile, sender=User)

class Incident(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True)
    transmissions = models.ManyToManyField(Transmission, blank=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  # Dont change if already set
            self.slug = slugify(self.name)
        super(Incident, self).save(*args, **kwargs)


class MessagePopUp(models.Model):
    mesg_type = models.CharField(max_length=1, choices=choice.MESG_CHOICES, unique=True)
    mesg_html = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.mesg_html
