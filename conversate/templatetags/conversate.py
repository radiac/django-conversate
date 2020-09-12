"""
Conversate template tags
"""
import time

from django import template

register = template.Library()


@register.filter
def naturaltimestamp(value):
    """
    For timestamp values shows how many seconds, minutes or hours ago
    compared to current timestamp

    Similar to naturaltime in django.contrib.humanize, but operates on
    a timestamp float instead of a datetime (which must be in the past),
    doesn't say "ago", and makes no attempt at i18n
    """
    # Timestamp is a float, or could have been cast to an int
    if not isinstance(value, (float, int)):
        return value

    now = time.time()

    # Catch future values - server time has gone into the past
    if value > now:
        return "now"

    delta = int(now - value)

    return naturaltimedelta(delta)


@register.filter
def naturaltimedelta(delta):
    if delta < 0:
        return "never"

    elif delta < 60:
        term = "second"

    elif delta < 60 * 60:
        delta /= 60
        term = "minute"

    elif delta < 60 * 60 * 24:
        delta /= 60 * 60
        term = "hour"

    else:
        delta /= 60 * 60 * 24
        term = "day"

    return "%s %s%s" % (
        int(delta),
        term,
        "" if delta == 1 else "s",
    )
