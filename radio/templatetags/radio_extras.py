from django import template
from django.conf import settings

register = template.Library()

# anonymous time seting
@register.simple_tag()
def settings_anonymous_time():
    return getattr(settings, 'ANONYMOUS_TIME', 0)
