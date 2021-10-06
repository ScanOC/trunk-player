import random
import json

from django import template
from django.conf import settings

from radio.models import SiteOption
from radio import __fullversion__ as VERSION

register = template.Library()

# Build json value to pass as js config
@register.simple_tag()
def trunkplayer_js_config(user):
    js_settings = getattr(settings, 'JS_SETTINGS', None)
    js_json = {}
    if js_settings:
        for setting in js_settings:
                set_val = getattr(settings, setting, '')
                js_json[setting] = set_val
    for opt in SiteOption.objects.filter(javascript_visible=True):
        js_json[opt.name] = opt.value_boolean_or_string()
    js_json['user_is_staff'] = user.is_staff
    if user.is_authenticated:
        js_json['user_is_authenticated'] = True
    else:
        js_json['user_is_authenticated'] = False
    js_json['radio_change_unit'] = user.has_perm('radio.change_unit')
    js_json['download_audio'] = user.has_perm('radio.download_audio')
    js_json['VERSION'] = VERSION
    return json.dumps(js_json)
