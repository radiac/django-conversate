"""
Conversate models
"""

import time

from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone


class Room(models.Model):
    title   = models.CharField(
        max_length=255, help_text="Title of the room",
    )
    slug    = models.SlugField(
        unique=True, help_text="Slug for the room",
    )
    users   = models.ManyToManyField(
        'auth.User', through='RoomUser', related_name='conversate_rooms',
    )

    class Meta:
        ordering = ('title',)
        
    def __unicode__(self):
        return u'%s' % self.title
    
    def get_absolute_url(self):
        return reverse(
            'conversate-room',
            kwargs={'room_slug': self.slug}
        )
    

class RoomUser(models.Model):
    room        = models.ForeignKey(Room)
    user        = models.ForeignKey('auth.User')
    
    # State
    last_seen   = models.DateTimeField(
        blank=True, null=True, help_text="Last seen",
    )
    has_focus   = models.BooleanField(
        default=False, help_text="If the user's window has focus",
    )
    last_spoke  = models.DateTimeField(
        blank=True, null=True, help_text="Last spoke",
    )
    inactive_from = models.DateTimeField(
        blank=True, null=True, help_text="User has left if no poll before this time",
    )
    last_mail_alert = models.DateTimeField(
        blank=True, null=True, help_text="Last time a mail alert was sent",
    )
    
    # Preferences
    colour      = models.CharField(
        max_length=6, help_text="Hex colour code", default="000000",
    )
    alert       = models.BooleanField(
        default=True, help_text="Visual alert when activity while not focused",
    )
    mail_alert  = models.BooleanField(
        default=False, help_text="Send e-mail alert when activity while offline",
    )

    class Meta:
        ordering = ('room', 'user__username',)
        
    def __unicode__(self):
        return u'%s/%s' % (self.room, self.user)
    
    def is_active(self, now=None):
        if not now:
            now = timezone.now()
        if self.inactive_from and self.inactive_from >= now:
            return True
        return False
        
    def can_mail_alert(self, now=None):
        if not now:
            now = timezone.now()
        
        if (self.mail_alert
            and self.user.email
            and not self.is_active(now)
            and (not self.last_mail_alert or self.last_seen > self.last_mail_alert)
        ):
            return True
        return False

class Message(models.Model):
    room        = models.ForeignKey(Room, related_name='messages')
    user        = models.ForeignKey('auth.User', related_name='conversate_messages')
    timestamp   = models.IntegerField()
    content     = models.TextField()
    
    class Meta:
        ordering = ('timestamp',)
    
    def __unicode__(self):
        return u'%s/%s %s' % (self.room, self.user, self.timestamp)
    
    def save(self, *args, **kwargs):
        """
        Force timestamp to now
        """
        self.timestamp = int(time.time())
        super(Message, self).save(*args, **kwargs)
