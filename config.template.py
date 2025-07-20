# -- WiFi Configuration --
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# -- Monitoring Configuration --
MONITOR_LATITUDE = 51.5074 # London
MONITOR_LONGITUDE = -0.1278 # London
MONITOR_RADIUS_KM = 500
CHECK_INTERVAL_MINUTES = 5
API_QUERY_PERIOD_MINUTES = 60
MIN_MAGNITUDE = 0

# -- Time Configuration --
TIMEZONE_OFFSET_HOURS = 2  # Central European Summer Time (Spain)
DO_NOT_DISTURB_START_HOUR = 23
DO_NOT_DISTURB_END_HOUR = 9

# -- Display Configuration --
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
PLACE_NAME_MAX_LENGTH = 25
ERROR_MESSAGE_MAX_LENGTH = 100 