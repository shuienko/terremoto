import M5
import time
from config import (
    FONT, LINE_HEIGHT, STARTUP_DISPLAY_DELAY, TIMEZONE_OFFSET_HOURS
)

# -- UI Colors --
COLOR_BLACK = 0x000000
COLOR_WHITE = 0xFFFFFF
COLOR_GREEN = 0x006400
COLOR_BLUE = 0x0000FF
COLOR_DARK_BLUE = 0x00008B

# -- Message Formats --
MESSAGES = {
    "STARTUP": "SIMPLE CLOCK\n\nStarting...\n\nTimezone: UTC{:+d}",
}

# Internal UI state to minimize redraw/flicker
_UI_INITIALIZED = False
_SCREEN_WIDTH = 0
_SCREEN_HEIGHT = 0
_TITLE_HEIGHT = 40
_TIME_Y = 0
_TIME_X = 0
_MAX_TIME_WIDTH = 0
_LAST_TIME_STR = None
_TIME_AREA_HEIGHT = 90  # approximate height for DejaVu72; generous to fully clear


def _init_clock_ui():
    global _UI_INITIALIZED, _SCREEN_WIDTH, _SCREEN_HEIGHT, _TIME_Y, _TIME_X, _MAX_TIME_WIDTH

    try:
        M5.Lcd.clear(COLOR_BLACK)

        _SCREEN_WIDTH = M5.Display.width()
        _SCREEN_HEIGHT = M5.Display.height()

        # Draw static title bar once
        M5.Lcd.fillRect(0, 0, _SCREEN_WIDTH, _TITLE_HEIGHT, COLOR_GREEN)
        M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu18)
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_GREEN)
        title = "= TIME NOW ="
        title_width = M5.Lcd.textWidth(title)
        M5.Lcd.drawString(title, (_SCREEN_WIDTH - title_width) // 2, (_TITLE_HEIGHT - 18) // 2)

        # Prepare metrics for time rendering
        M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu72)
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_BLACK)
        _MAX_TIME_WIDTH = M5.Lcd.textWidth("88:88")  # widest likely HH:MM in proportional font
        _TIME_X = (_SCREEN_WIDTH - _MAX_TIME_WIDTH) // 2  # stable centering independent of digits
        _TIME_Y = (_SCREEN_HEIGHT + _TITLE_HEIGHT) // 2 - 36

        _UI_INITIALIZED = True
    except Exception as e:
        print("LCD Init Error:", e)


def display_clock(time_str):
    """Display the current time in HH:MM format with minimal flicker"""
    global _LAST_TIME_STR
    print("Displaying time:", time_str)

    try:
        if not _UI_INITIALIZED:
            _init_clock_ui()

        # Avoid redundant redraws
        if time_str == _LAST_TIME_STR:
            return

        # Clear only the time area using fixed max width to avoid leftovers when width shrinks
        clear_y = max(_TITLE_HEIGHT, _TIME_Y - (_TIME_AREA_HEIGHT // 2))
        M5.Lcd.fillRect(_TIME_X, clear_y, _MAX_TIME_WIDTH, _TIME_AREA_HEIGHT, COLOR_BLACK)

        # Draw the time
        M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu72)
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_BLACK)
        M5.Lcd.drawString(time_str, _TIME_X, _TIME_Y)

        _LAST_TIME_STR = time_str

    except Exception as e:
        print("LCD Error:", e)


def show_startup_message():
    """Display startup message"""
    startup_msg = MESSAGES["STARTUP"].format(TIMEZONE_OFFSET_HOURS)
    print("Display:", startup_msg)
    
    try:
        M5.Lcd.clear(COLOR_BLACK)
        
        lines = startup_msg.split('\n')
        title = lines[0]
        body_text = "\n".join(lines[1:])

        screen_width = M5.Display.width()
        screen_height = M5.Display.height()

        # --- Draw Title Bar ---
        title_height = 30
        M5.Lcd.fillRect(0, 0, screen_width, title_height, COLOR_DARK_BLUE)

        # --- Draw Title Text ---
        M5.Lcd.setFont(M5.Lcd.FONTS.DejaVu18)
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_DARK_BLUE)
        title_width = M5.Lcd.textWidth(title)
        M5.Lcd.drawString(title, (screen_width - title_width) // 2, (title_height - 18) // 2)

        # --- Draw Body Text ---
        M5.Lcd.setFont(getattr(M5.Lcd.FONTS, FONT))
        M5.Lcd.setTextColor(COLOR_WHITE, COLOR_BLACK)

        body_lines = body_text.strip().split('\n')
        max_lines = 8

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