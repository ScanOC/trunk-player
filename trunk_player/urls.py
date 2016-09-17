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
router.register(r'talkgroups', views.TalkGroupViewSet)
router.register(r'scanlist', views.ScanListViewSet)


urlpatterns = [
    url('^$', TemplateView.as_view(template_name='radio/index_beta.html')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^api_v1/tg/(?P<filter_val>[+\w-]+)/$', views.TalkGroupFilterViewSet.as_view()),
    url(r'^api_v1/scan/(?P<filter_val>[+\w-]+)/$', views.ScanViewSet.as_view()),
    url(r'^api_v1/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^(tg|scan)/(.*)/$',TemplateView.as_view(template_name='radio/player_main.html')),
    url(r'^scan/$', RedirectView.as_view(url='/scan/default/', permanent=False)),
    url(r'^userscan/$', TemplateView.as_view(template_name='radio/player_userscan.html')),
    url(r'^talkgroups/$', views.TalkGroupList.as_view()),
    url(r'^audio/(?P<slug>[-\w]+)/$',views.TransDetailView.as_view(), name='trans'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/success/$', views.register_success),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
