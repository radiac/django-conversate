"""
Conversate views
"""
import datetime
import time

from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from conversate import settings, utils, models, forms
from conversate.decorators import room_required


@login_required
def index(request):
    """
    List of rooms
    """
    if request.user.is_superuser:
        rooms = models.Room.objects.all()
    else:
        rooms = request.user.conversate_rooms.all()
    
    return render(request, 'conversate/index.html', {
        'conversate_settings': utils.get_template_settings(),
        'title':    'Rooms',
        'rooms':    rooms,
    })


@room_required
def room(request, room, room_slug):
    """
    Show a room
    """
    # Get room messages
    room_user = _update_room_user(request, room)
    messages = room.messages.all()
    
    # Paginate
    msg_count = messages.count()
    remaining = 0
    if msg_count > settings.PAGE_SIZE:
        remaining = msg_count - settings.PAGE_SIZE
        messages = messages[remaining:]
    
    # Need all messages now, force lookup
    # Need last message for javascript
    messages = list(messages)
    first_message = messages[0] if len(messages) > 0 else None
    last_message = messages[-1] if len(messages) > 0 else None
    
    return render(request, 'conversate/room.html', {
        'conversate_settings': utils.get_template_settings(
            room, room_user, extra={
                'first':    first_message.pk,
                'last':     last_message.pk,
                'remaining':    remaining,
            }
        ),
        'title':    room.title,
        'room':     room,
        'form':     forms.MessageForm(),
        'settings': forms.SettingsForm(instance=room_user),
        'room_messages': messages,
        'room_users':    _room_users(room, request.user),
    })


@room_required
def send(request, room, room_slug):
    """
    Process a message submission
    """
    spoke = False
    if request.POST:
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.user = request.user
            message.save()
            spoke = True
            
    _update_room_user(request, room, spoke=spoke)
    _mail_alert(request, room)
    
    return HttpResponseRedirect(
        reverse('conversate-room', kwargs={'room_slug': room_slug})
    )

@room_required
def update_settings(request, room, room_slug):
    """
    Process a settings change request
    """
    room_user = _update_room_user(request, room)
    if request.POST:
        form = forms.SettingsForm(request.POST)
        if form.is_valid():
            for key, val in form.cleaned_data.items():
                setattr(room_user, key, val)
            room_user.save()
    
    return HttpResponseRedirect(
        reverse('conversate-room', kwargs={'room_slug': room_slug})
    )

@room_required
def api_base(request, room, room_slug):
    """
    Base API URL
    Currently just used to reverse for JavaScript
    """
    raise Http404


@room_required
def api_check(request, room, room_slug):
    """
    API: check for new messages
    """
    return _api_check(
        request, room, room_slug,
        last_pk=request.POST.get('last', None)
    )
    
def _mail_alert(request, room):
    """
    Send any mail alerts
    """
    now = datetime.datetime.now()
    for room_user in models.RoomUser.objects.filter(room=room):
        if room_user.can_mail_alert(now):
            send_mail(
                'Conversate activity in %s' % room,
                (
                    'There has been conversate activity in the room "%(room)s"'
                    ' since you last checked in.\n\n'
                    '  %(url)s\n'
                ) % {
                    'room': room,
                    'url':  request.build_absolute_uri(
                        reverse('conversate-room', kwargs={'room_slug': room.slug})
                    ),
                },
                settings.EMAIL_FROM,
                [room_user.user.email],
                fail_silently=True,
            )
            room_user.last_mail_alert = now
            room_user.save()


def _room_users(room, user):
    """
    Internal function to get a list of other room users
    """
    now = datetime.datetime.now()
    room_users = []
    for room_user in models.RoomUser.objects.filter(room=room):
        # Calc last seen/spoke
        last_seen = -1
        last_spoke = -1
        if room_user.last_seen:
            last_seen_delta = now - room_user.last_seen
            last_seen = last_seen_delta.seconds + (last_seen_delta.days * 24 * 60 * 60)
        if room_user.last_seen:
            last_spoke_delta = now - room_user.last_spoke
            last_spoke = last_spoke_delta.seconds + (last_spoke_delta.days * 24 * 60 * 60)
        
        room_users.append({
            'username': room_user.user.username,
            'active':       room_user.is_active(now=now),
            'has_focus':    room_user.has_focus,
            'last_seen':    last_seen,
            'last_spoke':   last_spoke,
            'colour':       room_user.colour,
        })
    return room_users
    
def _update_room_user(request, room, has_focus=False, spoke=False):
    # Update user's last seen
    room_user = models.RoomUser.objects.get(room=room, user=request.user)
    now = datetime.datetime.now()
    room_user.last_seen = now
    room_user.inactive_from = now + datetime.timedelta(seconds=settings.DISCONNECT_AT)
    if spoke:
        room_user.last_spoke = now
    room_user.has_focus = has_focus
    room_user.save()
    return room_user
    
def _api_check(request, room, room_slug, last_pk, spoke=False):
    """
    Interal function to check for new messages and return a json response
    """
    if not last_pk:
        return utils.jsonResponse({
            'success':  False,
            'error':    'No pointer provided',
        })
        
    # Register the ping
    has_focus = request.POST.get('hasFocus', 'false') == 'true'
    _update_room_user(request, room, has_focus, spoke)
    
    # Prep list of messages
    messages = list(room.messages.filter(pk__gt=last_pk))
    data = [
        {
            'pk':   msg.pk,
            'time': msg.timestamp,
            'user': msg.user.username,
            'content':  msg.content,
        } for msg in messages
    ]
    
    return utils.jsonResponse({
        'success':  True,
        'last':     last_pk if not messages else messages[-1].pk,
        'time':     int(time.time()),
        'messages': data,
        'users':    _room_users(room, request.user),
    })


@room_required
def api_send(request, room, room_slug):
    """
    API: send message
    """
    if request.POST:
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.user = request.user
            message.save()
            
            # Get response and update users before sending mail alerts
            response = _api_check(
                request, room, room_slug,
                last_pk=request.POST.get('last', None),
                spoke=True,
            )
            _mail_alert(request, room)
            
            return response
        else:
            error = 'Invalid message'
    else:
        error = 'Invalid request'
    
    return utils.jsonResponse({
        'success':  False,
        'error':    error,
    })


@room_required
def api_history(request, room, room_slug):
    first_pk = request.POST.get('first', None)
    messages = room.messages.filter(pk__lt=first_pk)
    
    # Paginate
    msg_count = messages.count()
    remaining = 0
    if msg_count > settings.PAGE_SIZE:
        remaining = msg_count - settings.PAGE_SIZE
        messages = messages[remaining:]
    
    # Need all messages now, force lookup
    # Need last message for javascript
    messages = list(messages)
    first_message = messages[0] if len(messages) > 0 else None
    data = [
        {
            'pk':   msg.pk,
            'time': msg.timestamp,
            'user': msg.user.username,
            'content':  msg.content,
        } for msg in messages
    ]
    
    return utils.jsonResponse({
        'success':  True,
        'first':    first_message.pk,
        'remaining':    remaining,
        'messages':     data,
    })
