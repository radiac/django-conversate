from django.conf import settings

# Number of lines to show on a page
PAGE_SIZE = getattr(settings, "CONVERSATE_PAGE_SIZE", 100)

# Time until UI decides user is idle (in ms)
IDLE_AT = getattr(settings, "CONVERSATE_IDLE_AT", 60 * 1000)

# Minimum poll interval (in ms)
POLL_MIN = getattr(settings, "CONVERSATE_POLL_MIN", 5 * 1000)

# Maximum poll interval (in ms)
POLL_MAX = getattr(settings, "CONVERSATE_POLL_MAX", 60 * 1000)

# Amount to increase poll interval by when there is no activity (in ms)
POLL_STEP = getattr(settings, "CONVERSATE_POLL_STEP", 5 * 1000)

# If True, Conversate's JavaScript will control the layout:
#   - changes the container element to position:relative and padding:0
#   - maximises container element's height into available space in the window
#   - makes the conversation scroll in place
#   - moves the input field to the bottom of the container
CONTROL_LAYOUT = getattr(settings, "CONVERSATE_CONTROL_LAYOUT", True)

# How long before marking the user as disconnected (in secs)
# Defaults to POLL_MAX plus 30 seconds
DISCONNECT_AT = getattr(
    settings,
    "CONVERSATE_DISCONNECT_AT",
    (POLL_MAX / 1000) + 30,
)

# From address
EMAIL_FROM = getattr(
    settings,
    "CONVERSATE_EMAIL_FROM",
    getattr(settings, "DEFAULT_FROM_EMAIL"),
)

# Path to the private file store
#
# This should be a private dir outside the main site structure.
#
# Defaults to media root so it will work out of the box, but this has security
# implications - permission checks can be bypassed.
# Default: MEDIA_ROOT
STORE_ROOT = getattr(settings, "CONVERSATE_STORE_ROOT", settings.MEDIA_ROOT)
