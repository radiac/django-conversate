from django.contrib import admin

from . import models


class RoomUserAdmin(admin.TabularInline):
    model = models.RoomUser


class RoomAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
    ]
    inlines = [
        RoomUserAdmin,
    ]


admin.site.register(models.Room, RoomAdmin)
