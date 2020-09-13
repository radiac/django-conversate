"""
Conversate URLs
"""
from django.urls import re_path

from . import views

app_name = "conversate"

urlpatterns = [
    re_path(
        r"^$",
        views.index,
        name="index",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/$",
        views.room,
        name="room",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/send/$",
        views.send,
        name="send",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/file/(?P<message_id>\d+)/$",
        views.download_file,
        name="file",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/settings/$",
        views.update_settings,
        name="settings",
    ),
    #
    # JSON API
    #
    re_path(
        r"^(?P<room_slug>[-\w]+)/api/$",
        views.api_base,
        name="api_base",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/api/poll/$",
        views.api_check,
        name="api_check",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/api/send/$",
        views.api_send,
        name="api_send",
    ),
    re_path(
        r"^(?P<room_slug>[-\w]+)/api/history/$",
        views.api_history,
        name="api_history",
    ),
]
