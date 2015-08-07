"""
Conversate URLs
"""

try:
    from django.conf.urls import include, patterns, url
except ImportError:
    from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('conversate.views',
    url(r'^$',
        'index', name='conversate-index',
    ),
    
    url(r'^(?P<room_slug>[-\w]+)/$',
        'room', name='conversate-room',
    ),
    
    url(r'^(?P<room_slug>[-\w]+)/send/$',
        'send', name='conversate-send',
    ),
    
    url(r'^(?P<room_slug>[-\w]+)/settings/$',
        'update_settings', name='conversate-settings',
    ),
    
    
    #
    # JSON API
    #
    
    url(r'^(?P<room_slug>[-\w]+)/api/$',
        'api_base', name='conversate-api_base',
    ),
    url(r'^(?P<room_slug>[-\w]+)/api/poll/$',
        'api_check', name='conversate-api_check',
    ),
    url(r'^(?P<room_slug>[-\w]+)/api/send/$',
        'api_send', name='conversate-api_send',
    ),
    url(r'^(?P<room_slug>[-\w]+)/api/history/$',
        'api_history', name='conversate-api_history',
    ),
    
)
