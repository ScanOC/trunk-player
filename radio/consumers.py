import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
from .models import ScanList, TalkGroup

log = logging.getLogger(__name__)

@channel_session
def ws_connect(message):
    try:
        prefix, tg_type, label = message['path'].strip('/').split('/')
        if prefix != 'ws-calls':
            log.debug('invalid ws path=%s', message['path'])
            return
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return

    log.debug('connect %s=%s client=%s:%s', 
        tg_type, label, message['client'][0], message['client'][1])
   
    label_list = label.split('+')
    for new_label in label_list: 
        channel_name = 'livecall-{}-{}'.format(tg_type, new_label)
        log.debug("Connected to channel {}".format(channel_name))
        Group(channel_name, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['scan'] = label

@channel_session
def ws_receive(message):
    try:
        label = message.channel_session['scan']
        
        scan = ScanList.objects.get(name=label)
    except KeyError:
        log.debug('no scanlist in channel_session')
        return
    except ScanList.DoesNotExist:
        log.debug('recieved message, but scablist does not exist label=%s', label)
        return

    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return
    
@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['scan']
        scan = ScanList.objects.get(name=label)
        Group('livecall-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, ScanList.DoesNotExist):
        pass
