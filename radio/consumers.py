import re
import json
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ScanList, TalkGroup

logging.basicConfig(format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)


class RadioConsumer(WebsocketConsumer):
    def connect(self):
        try:
            tg_type =  self.scope['url_route']["kwargs"]["tg_type"]
            label = self.scope['url_route']["kwargs"]["label"]
        except:
            # setup fake channel so the javascript does not try and reconnect
            tg_type = 'junk'
            label = 'junk'
            log.error('user %s invalid ws path=%s setting up fake channel', self.scope['user'], self.scope['url_route'])

        # log.error('user %s connect %s=%s client=%s:%s', 
        #     message.user, tg_type, label, message['client'][0], message['client'][1])
    
        label_list = label.split('+')
        for new_label in label_list: 
            channel_name = 'livecall-{}-{}'.format(tg_type, new_label)
            log.error("User {} Connected to channel {}".format(self.scope['user'], channel_name))
            async_to_sync(self.channel_layer.group_add)(
                channel_name,
                self.channel_name
            )
            
        self.accept()
        self.label=label

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.label,
                self.channel_name
            )
        except (KeyError, ScanList.DoesNotExist):
            pass

        
        # Leave room group
        

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        try:           
            scan = ScanList.objects.get(name=self.label)
        except KeyError:
            log.error('no scanlist in channel_session')
            return
        except ScanList.DoesNotExist:
            log.error('recieved message, but scanlist does not exist label=%s', self.label)
            return

        # conform to the expected message format.
        try:
            data = json.loads(message)
        except ValueError:
            log.error("ws message isn't json text=%s", text_data)
            return
            

    def radio_message(self, event):
        message = event['text']

        # Send message to WebSocket
        self.send(text_data=(message))