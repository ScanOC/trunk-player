import random

from django import template
from django.conf import settings

register = template.Library()

# anonymous time seting
@register.simple_tag()
def settings_anonymous_time():
    return getattr(settings, 'ANONYMOUS_TIME', 0)

# Amazon adds
@register.simple_tag()
def settings_amazon_adds():
    return getattr(settings, 'AMAZON_ADDS', False)

# All Amazon Settings
@register.simple_tag()
def settings_amazon_ad(value):
    if value.startswith("AMAZON_AD"): # Only expose amazon settings
        if value == 'AMAZON_AD_FALL_BACK_SEARCH': # Pick from the list
            return random.choice(getattr(settings, value, False))
        return getattr(settings, value, False)
    return None

# Allow settings in VISABLE_SETTINGS to be aviliable
@register.simple_tag()
def get_setting(value):
    visable_settings = getattr(settings, 'VISABLE_SETTINGS', None)
    if value in visable_settings:
        return getattr(settings, value, False)
    return None
    
