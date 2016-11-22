import random
import json

from django import template
from django.conf import settings

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
    js_json['user_is_staff'] = user.is_staff
    if user.is_authenticated():
        js_json['user_is_authenticated'] = True
    else:
        js_json['user_is_authenticated'] = False
    js_json['radio_change_unit'] = user.has_perm('radio.change_unit')
    return json.dumps(js_json)
