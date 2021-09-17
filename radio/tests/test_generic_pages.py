import json

from django.test import TestCase
from django.test import Client
from django.urls import reverse

from radio.models import WebHtml
from radio.views import Generic

class GenericHTMLTests(TestCase):
    """
    Test the generic pages
    """
    def setUp(self):
        #self.factory = RequestFactory()
        page1 = WebHtml.objects.create(name='FirstPage', bodytext='Test1')

    def test_page_exists(self):
        client = Client()
        response = client.get(reverse('pages',  kwargs={'page_name': 'FirstPage'}))
        self.assertEquals(response.status_code, 200)
