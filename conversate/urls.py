"""
Conversate URLs
"""
from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^$',
        views.index,
        name='index',
    ),

    url(
        r'^(?P<room_slug>[-\w]+)/$',
        views.room,
        name='room',
    ),

    url(
        r'^(?P<room_slug>[-\w]+)/send/$',
        views.send,
        name='send',
    ),

    url(
        r'^(?P<room_slug>[-\w]+)/settings/$',
        views.update_settings,
        name='settings',
    ),


    #
    # JSON API
    #

    url(
        r'^(?P<room_slug>[-\w]+)/api/$',
        views.api_base,
        name='api_base',
    ),
    url(
        r'^(?P<room_slug>[-\w]+)/api/poll/$',
        views.api_check,
        name='api_check',
    ),
    url(
        r'^(?P<room_slug>[-\w]+)/api/send/$',
        views.api_send,
        name='api_send',
    ),
    url(
        r'^(?P<room_slug>[-\w]+)/api/history/$',
        views.api_history,
        name='api_history',
    ),
]
