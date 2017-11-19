import json

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, override_settings
from django.test import RequestFactory
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory

from radio.models import Transmission, TalkGroup, System, TalkGroupAccess, TalkGroupWithSystem, Profile
from radio.views import TalkGroupFilterViewSet

class TalkgroupRestictTests(TestCase):
    """
    Test that only user 1 can see the Test TG 1 TalkGroup when access control is on
    """
    def setUp(self):
        self.factory = RequestFactory()
        user1 = User.objects.create_user('user1', 'user1@example.com', 'pass1')
        User.objects.create_user('user2', 'user2@example.com', 'pass2')
        tg1 = TalkGroup.objects.create( dec_id=100, alpha_tag='Test TG 1' )
        Transmission.objects.create( 
            start_datetime=timezone.now(),
            audio_file='100-1511023743_8.57213e+08',
            audio_file_type='mp3',
            audio_file_url_path='/',
            talkgroup=100,
            talkgroup_info = tg1,
            freq=0,
            )
        tg1_sys = TalkGroupWithSystem.objects.get(pk=tg1.pk)
        tg_access1 = TalkGroupAccess.objects.create(name='Demo1')
        tg_access1.talkgroups.add(tg1_sys)
        user1.profile.talkgroup_access.add(tg_access1)

    def test_talkgroup_exists(self):
        tg = TalkGroup.objects.get(alpha_tag = 'Test TG 1')
        self.assertEquals(str(tg), 'Test TG 1')

    @override_settings(ACCESS_TG_RESTRICT=False)
    def test_talkgroup_access_open(self):
        anon = User.objects.get
        response = self.client.get('/api_v1/tg/test-tg-1/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(str(response.content, encoding='utf8'))
        self.assertEquals(data['count'], 1)

    @override_settings(ACCESS_TG_RESTRICT=True)
    def test_talkgroup_access_user1(self):
        user = User.objects.get(username='user1')
        request = self.factory.get('/api_v1/tg/test-tg-1/')
        request.user = user
        response = TalkGroupFilterViewSet.as_view()(request, filter_val='test-tg-1').render()
        #print(response.content)
        data = json.loads(str(response.content, encoding='utf8'))
        self.assertEquals(data['count'], 1)

    @override_settings(ACCESS_TG_RESTRICT=True)
    def test_talkgroup_access_user2(self):
        user = User.objects.get(username='user2')
        request = self.factory.get('/api_v1/tg/test-tg-1/')
        request.user = user
        response = TalkGroupFilterViewSet.as_view()(request, filter_val='test-tg-1').render()
        #print(response.content)
        data = json.loads(str(response.content, encoding='utf8'))
        self.assertEquals(data['count'], 0)

