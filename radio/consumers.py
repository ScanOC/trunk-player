import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from .models import ScanList, TalkGroup

logging.basicConfig(format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

@channel_session_user_from_http
def ws_connect(message):
    try:
        prefix, tg_type, label = message['path'].strip('/').split('/')
        if prefix != 'ws-calls':
            log.error('user %s invalid ws path=%s', message.user, message['path'])
            return
    except ValueError:
        # setup fake channel so the javascript does not try and reconnect
        tg_type = 'junk'
        label = 'junk'
        log.error('user %s invalid ws path=%s setting up fake channel', message.user, message['path'])

    log.error('user %s connect %s=%s client=%s:%s', 
        message.user, tg_type, label, message['client'][0], message['client'][1])
   
    label_list = label.split('+')
    for new_label in label_list: 
        channel_name = 'livecall-{}-{}'.format(tg_type, new_label)
        log.error("User {} Connected to channel {}".format(message.user, channel_name))
        message.reply_channel.send({"accept": True})
        Group(channel_name, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['scan'] = label

@channel_session
def ws_receive(message):
    try:
        label = message.channel_session['scan']
        
        scan = ScanList.objects.get(name=label)
    except KeyError:
        log.error('no scanlist in channel_session')
        return
    except ScanList.DoesNotExist:
        log.error('recieved message, but scanlist does not exist label=%s', label)
        return

    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.error("ws message isn't json text=%s", text)
        return
    
@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['scan']
        scan = ScanList.objects.get(name=label)
        Group('livecall-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, ScanList.DoesNotExist):
        pass
