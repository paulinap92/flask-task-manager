"""
Timezone configuration module.

Defines the default timezone used throughout the application.
"""

from zoneinfo import ZoneInfo

# Fixed timezone for all datetime operations in the application.
CURRENT_TIMEZONE = ZoneInfo("Europe/Warsaw")
