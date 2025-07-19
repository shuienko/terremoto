# -- WiFi Configuration --
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# -- Monitoring Configuration --
MONITOR_LATITUDE = 40.4168  # Madrid
MONITOR_LONGITUDE = -3.7038  # Madrid
MONITOR_RADIUS_KM = 1000
CHECK_INTERVAL_MINUTES = 5
MIN_MAGNITUDE = 2.5

# -- Time Configuration --
TIMEZONE_OFFSET_HOURS = 2  # Central European Summer Time (Spain)

# -- Display Configuration --
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
TEXT_SIZE = 2  # Default text size multiplier (1, 2, 3...)
LINE_HEIGHT = 20  # Line height in pixels for multi-line text
MAX_LINES = 10  # Max lines to display to avoid screen overflow
FONT = "DejaVu18"
STARTUP_DISPLAY_DELAY = 5

# -- Network & API Configuration --
WIFI_MAX_RETRIES = 3
WIFI_RETRY_DELAY = 5
WIFI_MAX_WAIT = 10
HTTP_TIMEOUT = 30
EMSC_BASE_URL = "https://www.seismicportal.eu/fdsnws/event/1/query"

# -- Data & Formatting Configuration --
EARTH_RADIUS_KM = 6371
PLACE_NAME_MAX_LENGTH = 20
ERROR_MESSAGE_MAX_LENGTH = 100 