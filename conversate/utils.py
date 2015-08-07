"""
Conversate utils
"""
import time
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from conversate import settings


def jsonResponse(data):
    """
    Return a JSON HttpResponse
    """
    return HttpResponse(
        json.dumps(data, cls=DjangoJSONEncoder),
        content_type='application/json',
    )

def get_template_settings(
    room=None, room_user=None, extra=None,
):
    config = {
        'alertEnabled': room_user.alert if room_user else False,
        'serverTime':   int(time.time()),
    }
    
    # Add API calls for room
    if room:
        config['apiCheck'] = reverse(
            'conversate-api_check', kwargs={'room_slug': room.slug}
        )
        config['apiSend'] = reverse(
            'conversate-api_send', kwargs={'room_slug': room.slug}
        )
        config['apiHistory'] = reverse(
            'conversate-api_history', kwargs={'room_slug': room.slug}
        )
    
    # Allow for custom stuff
    if extra:
        config.update(extra)
    
    # Copy across settings
    for setting in dir(settings):
        if not setting.isupper():
            continue
        titled = ''.join(chunk.capitalize() for chunk in setting.split('_'))
        config[titled[:1].lower() + titled[1:]] = getattr(settings, setting)
    
    return {
        'add_jquery':   settings.ADD_JQUERY,
        'config':       json.dumps(config, cls=DjangoJSONEncoder),
    }
