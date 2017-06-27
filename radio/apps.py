from importlib import import_module

from django.apps import AppConfig

class RadioConfig(AppConfig):
    name = 'radio'


    def ready(self):
        import_module("radio.receivers")
