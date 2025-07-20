import M5
import time
from config import (
    FONT, LINE_HEIGHT, MAX_LINES, MONITOR_LATITUDE, MONITOR_LONGITUDE,
    MONITOR_RADIUS_KM, STARTUP_DISPLAY_DELAY, API_QUERY_PERIOD_MINUTES,
    PLACE_NAME_MAX_LENGTH
)
from utils import format_event_time

# -- UI Colors --
COLOR_BLACK = 0x000000
COLOR_WHITE = 0xFFFFFF
COLOR_RED = 0xFF0000
COLOR_DARK_RED = 0x8B0000
COLOR_GREEN = 0x00FF00
COLOR_DARK_GREEN = 0x006400
COLOR_BLUE = 0x0000FF
COLOR_DARK_BLUE = 0x00008B
COLOR_YELLOW = 0xFFFF00
COLOR_DARK_YELLOW = 0xCCCC00

# -- Message Formats --
MESSAGES = {
    "STARTUP": "EARTHQUAKE MONITOR\n\nStarting...\n\nLat: {:.2f}\nLon: {:.2f}\nRadius: {}km",
    "WIFI_CONNECTING_ATTEMPT": "WIFI\nCONNECTING\n\nAttempt {}/{}",
    "WIFI_LOST": "WIFI LOST\n\nReconnecting...",
    "WIFI_FAILED": "WIFI FAILED\n\nRetrying in\n{} minutes",
    "TIME_SYNCED": "TIME SYNCED\n\n{}",
    "NTP_FAILED": "NTP FAILED\n\nWill use\nlast known time",
    "CONNECTION_ERROR": "CONNECTION\nERROR\n\nRetrying WiFi\n\nLast check: {}",
    "ALL_CLEAR": "== ALL CLEAR ==\n\nNo earthquakes\nin {}km radius\n\nWorldwide {}m: {}\nLast check: {}",
    "EARTHQUAKE": "!!! EARTHQUAKE !!!\n\nMag: {:.1f}\n{}\nDist: {:.0f}km\n\nTime: {}",
    "STOPPING": "STOPPING...",
    "RUNTIME_ERROR": "RUNTIME ERROR\n\n{}\n\nRestarting loop...",
}

def _display_template(text, title_bg_color):
    """A template for displaying messages with a colored title bar."""
    print("Display:", text)

    try:
        M5.Lcd.clear(COLOR_BLACK)

        lines = text.split('\n')
        title = lines[0]
        body_text = "\n".join(lines[1:])

        screen_width = M5.Display.width()
        screen_height = M5.Display.height()

        # --- Draw Title Bar ---
        title_height = 30
        M5.Lcd.fillRect(0, 0, screen_width, title_height, title_bg_color)

        # --- Draw Title Text ---
        M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu18)
        M5.Lcd.setTextColor(COLOR_WHITE, title_bg_color)
        title_width = M5.Lcd.textWidth(title)
        M5.Lcd.drawString(title, (screen_width - title_width) // 2, (title_height - 18) // 2)

        # --- Draw Body Text ---
        M5.Lcd.setFont(getattr(M5.Lcd.FONTS, FONT))
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_BLACK)

        body_lines = body_text.strip().split('\n')
        max_lines = MAX_LINES

        line_height = LINE_HEIGHT
        total_text_height = min(len(body_lines), max_lines) * line_height

        content_height = screen_height - title_height
        start_y = title_height + (content_height - total_text_height) // 2

        y = start_y
        for line in body_lines[:max_lines]:
            if line.strip():
                try:
                    text_width = M5.Lcd.textWidth(line)
                    x = max(0, (screen_width - text_width) // 2)
                except:
                    text_width = len(line) * 10
                    x = max(0, (screen_width - text_width) // 2)

                M5.Lcd.drawString(line, x, y)
            y += line_height

    except Exception as e:
        print("LCD Error:", e)

def display_info(text):
    _display_template(text, COLOR_DARK_BLUE)

def display_success(text):
    _display_template(text, COLOR_DARK_GREEN)

def display_warning(text):
    _display_template(text, COLOR_DARK_YELLOW)

def display_error(text):
    _display_template(text, COLOR_DARK_RED)

def display_earthquake_alert(text):
    _display_template(text, COLOR_RED)

def show_startup_message():
    """Display startup message with monitoring configuration"""
    startup_msg = MESSAGES["STARTUP"].format(
        MONITOR_LATITUDE, MONITOR_LONGITUDE, MONITOR_RADIUS_KM
    )
    display_info(startup_msg)
    time.sleep(STARTUP_DISPLAY_DELAY)

def format_earthquake_message(earthquake, total_found, check_timestamp):
    """Format message based on earthquake data"""
    if total_found == -1:
        return MESSAGES["CONNECTION_ERROR"].format(check_timestamp), "warning"
    elif not earthquake:
        return MESSAGES["ALL_CLEAR"].format(
            MONITOR_RADIUS_KM, API_QUERY_PERIOD_MINUTES, total_found, check_timestamp
        ), "success"
    else:
        # Show the provided earthquake
        place_short = earthquake['place'][:PLACE_NAME_MAX_LENGTH]
        event_time_str = format_event_time(earthquake.get('timestamp', ''))
        return MESSAGES["EARTHQUAKE"].format(
            earthquake['magnitude'],
            place_short,
            earthquake['distance'],
            event_time_str
        ), "alert" 