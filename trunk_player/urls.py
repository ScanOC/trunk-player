"""trunk_player URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin, auth
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from rest_framework import routers
from radio import views

router = routers.DefaultRouter()
router.register(r'transmission', views.TransmissionViewSet)
router.register(r'talkgroups', views.TalkGroupViewSet, base_name='talkgroups')
router.register(r'scanlist', views.ScanListViewSet)
router.register(r'menuscanlist', views.MenuScanListViewSet)
router.register(r'menutalkgrouplist', views.MenuTalkGroupListViewSet)


urlpatterns = [
    #url('^$', TemplateView.as_view(template_name='radio/index_beta.html')),
    url('^$', views.Generic, {'page_name': 'index'}, name='index'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api_v1/unit/(?P<filter_val>[+\w-]+)/$', views.UnitFilterViewSet.as_view()),
    url(r'^api_v1/tg/(?P<filter_val>[+\w-]+)/$', views.TalkGroupFilterViewSet.as_view()),
    url(r'^api_v1/scan/(?P<filter_val>[+\w-]+)/$', views.ScanViewSet.as_view()),
    url(r'^api_v1/inc/(?P<filter_val>[+\w-]+)/$', views.IncViewSet.as_view()),
    url(r'^api_v1/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^scan/(?P<name>.*)/details/$', views.ScanDetailsList, name='scan_details'),
    url(r'^(tg|scan|unit)/(.*)/$',TemplateView.as_view(template_name='radio/player_main.html')),
    url(r'^inc/(.*)/$',views.incident, name='incident'),
    url(r'^scan/$', RedirectView.as_view(url='/scan/default/', permanent=False)),
    url(r'^userscan/$', TemplateView.as_view(template_name='radio/player_userscan.html')),
    url(r'^about/$', views.Generic, {'page_name': 'about'}, name='about'),
    url(r'^page/(?P<page_name>.*)/$', views.Generic, name='pages'),
    url(r'^talkgroups/$', views.TalkGroupList.as_view()),
    url(r'^audio/(?P<slug>[-\w]+)/$',views.TransDetailView, name='trans'),
    url(r'^audio_download/(?P<slug>[-\w]+)/$',views.transDownloadView, name='download'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/success/$', views.register_success),
    url(r'^unitupdate/(?P<pk>\d+)/$', views.UnitUpdateView.as_view(), name='unitupdate'),
    url(r'^unitupdategood/$',  TemplateView.as_view(template_name='radio/unitupdategood.html')),
    url(r"^payments/", include("pinax.stripe.urls")),
    url(r'^upgrade/$', views.upgrade, name='upgrade'),
    url(r'^city/(?P<slug>[-\w]+)/$',views.cityDetailView, name='city_details'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if getattr(settings, 'SHOW_STRIPE_PLANS', False):
    urlpatterns = urlpatterns + [ url(r'^plans/$', views.plans, name='plans') ]
else:
    urlpatterns = urlpatterns + [ url(r'^plans/$', views.Generic, {'page_name': 'plans'}, name='plans') ]

