"""
Conversate models
"""
import os
import time

from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils import html, timezone

from commonmark import commonmark
from emoji import emojize

from . import settings


User = get_user_model()


class Room(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="Title of the room",
    )
    slug = models.SlugField(
        unique=True,
        help_text="Slug for the room",
    )
    users = models.ManyToManyField(
        User,
        through="RoomUser",
        related_name="conversate_rooms",
    )

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        return reverse("conversate:room", kwargs={"room_slug": self.slug})


class RoomUser(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # State
    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last seen",
    )
    has_focus = models.BooleanField(
        default=False,
        help_text="If the user's window has focus",
    )
    last_spoke = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last spoke",
    )
    inactive_from = models.DateTimeField(
        blank=True,
        null=True,
        help_text="User has left if no poll before this time",
    )
    last_mail_alert = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time a mail alert was sent",
    )

    # Preferences
    colour = models.CharField(
        max_length=6,
        help_text="Hex colour code",
        default="000000",
    )
    alert = models.BooleanField(
        default=True,
        help_text="Visual alert when activity while not focused",
    )
    mail_alert = models.BooleanField(
        default=False,
        help_text="Send e-mail alert when activity while offline",
    )

    class Meta:
        ordering = (
            "room",
            "user__username",
        )

    def __str__(self):
        return "%s/%s" % (self.room, self.user)

    def is_active(self, now=None):
        if not now:
            now = timezone.now()
        if self.inactive_from and self.inactive_from >= now:
            return True
        return False

    def can_mail_alert(self, now=None):
        if not now:
            now = timezone.now()

        if (
            self.mail_alert
            and self.user.email
            and not self.is_active(now)
            and (not self.last_mail_alert or self.last_seen > self.last_mail_alert)
        ):
            return True
        return False


file_store = FileSystemStorage(location=settings.STORE_ROOT)


def file_upload_to(item, filename):
    return os.path.join("conversate", item.room_id, filename)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="conversate_messages", on_delete=models.CASCADE
    )
    timestamp = models.IntegerField()
    content = models.TextField()
    file = models.FileField(
        storage=file_store, upload_to="conversate", blank=True, null=True
    )

    class Meta:
        ordering = ("timestamp",)

    def __str__(self):
        return "%s/%s %s" % (self.room, self.user, self.timestamp)

    def save(self, *args, **kwargs):
        """
        Force timestamp to now
        """
        if not self.timestamp:
            self.timestamp = int(time.time())
        super(Message, self).save(*args, **kwargs)

    def get_file_url(self):
        return reverse(
            "conversate:file",
            kwargs={"room_slug": self.room.slug, "message_id": self.id},
        )

    def render(self):
        as_safe = html.escape(self.content)
        as_emoji = emojize(as_safe, use_aliases=True)
        as_html = commonmark(as_emoji)

        if self.file:
            if "." in self.file.name:
                ext = self.file.name.rsplit(".", 1)[1].lower()
            else:
                ext = ""

            if ext in ["jpg", "jpeg", "png", "gif"]:
                label = f'<img src="{self.get_file_url()}">'
            else:
                label = self.file.name

            as_html += (
                f'<a href="{self.get_file_url()}" class="cnv_file" target="_blank">'
                f"{label}</a>"
            )
        return as_html
