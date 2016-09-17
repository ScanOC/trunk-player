import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trunk_player.settings")
channel_layer = channels.asgi.get_channel_layer()
