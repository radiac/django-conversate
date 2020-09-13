"""
Conversate decorators
"""

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import models


def room_required(fn):
    """
    View decorator to look up and validate a room slug
    Looks up room based on slug, or raises 404
    Checks the user has permission to access it, or raises PermissionDenied
    Passes Room instance to view as second argument
    """

    def wrapper(request, *args, **kwargs):
        # TODO: This risks leaking room names
        room = get_object_or_404(models.Room, slug=kwargs.get("room_slug", None))

        # Check logged in
        if not request.user.is_authenticated:
            # Make auth decorator fail to force user to login form
            return user_passes_test(lambda u: False)(lambda r: None)(request)

        # Check permission
        if (
            not request.user.is_superuser
            and request.user.conversate_rooms.filter(slug=room.slug).count() == 0
        ):
            raise PermissionDenied

        # Permission granted
        return fn(request, room, *args, **kwargs)

    return wrapper


def room_required_api(fn):
    """
    API decorator for room checks, returns JSON responses instead of error states
    """

    def wrapper(request, *args, **kwargs):
        try:
            room = models.Room.objects.get(slug=kwargs.get("room_slug", None))
        except models.Room.DoesNotExist:
            return JsonResponse({"success": False, "error": "Room does not exist"})

        # Check logged in
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "You need to log in"})

        # Check permission
        if (
            not request.user.is_superuser
            and request.user.conversate_rooms.filter(slug=room.slug).count() == 0
        ):
            return JsonResponse(
                {"success": False, "error": "You do not have permission"}
            )

        # Permission granted
        return fn(request, room, *args, **kwargs)

    return wrapper
