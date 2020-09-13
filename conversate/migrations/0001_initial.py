# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("timestamp", models.IntegerField()),
                ("content", models.TextField()),
            ],
            options={
                "ordering": ("timestamp",),
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(help_text=b"Title of the room", max_length=255),
                ),
                ("slug", models.SlugField(help_text=b"Slug for the room", unique=True)),
            ],
            options={
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="RoomUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "last_seen",
                    models.DateTimeField(help_text=b"Last seen", null=True, blank=True),
                ),
                (
                    "has_focus",
                    models.BooleanField(
                        default=False, help_text=b"If the user's window has focus"
                    ),
                ),
                (
                    "last_spoke",
                    models.DateTimeField(
                        help_text=b"Last spoke", null=True, blank=True
                    ),
                ),
                (
                    "inactive_from",
                    models.DateTimeField(
                        help_text=b"User has left if no poll before this time",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "last_mail_alert",
                    models.DateTimeField(
                        help_text=b"Last time a mail alert was sent",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "colour",
                    models.CharField(
                        default=b"000000", help_text=b"Hex colour code", max_length=6
                    ),
                ),
                (
                    "alert",
                    models.BooleanField(
                        default=True,
                        help_text=b"Visual alert when activity while not focused",
                    ),
                ),
                (
                    "mail_alert",
                    models.BooleanField(
                        default=False,
                        help_text=b"Send e-mail alert when activity while offline",
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        to="conversate.Room",
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("room", "user__username"),
            },
        ),
        migrations.AddField(
            model_name="room",
            name="users",
            field=models.ManyToManyField(
                related_name="conversate_rooms",
                through="conversate.RoomUser",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="room",
            field=models.ForeignKey(
                related_name="messages",
                to="conversate.Room",
                on_delete=models.deletion.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="user",
            field=models.ForeignKey(
                related_name="conversate_messages",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.deletion.CASCADE,
            ),
        ),
    ]
