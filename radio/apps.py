from importlib import import_module
from django.db.models.signals import post_migrate

from django.apps import AppConfig

def default_data_setup(sender, **kwargs):
    from django.contrib.auth.models import User
    try:
        anon = User.objects.get(username='ANONYMOUS_USER')
    except User.DoesNotExist:
        print('Adding ANONYMOUS_USER')
        anon = User.objects.create_user('ANONYMOUS_USER', 'anonymous_user@example.com')
        # Make the user un usable
        anon.set_unusable_password()
        anon.is_active = False
        anon.save()


class RadioConfig(AppConfig):
    name = 'radio'


    def ready(self):
        post_migrate.connect(default_data_setup, sender=self)
