import M5
import time
import config

def set_display_brightness():
    """Set display brightness based on Do Not Disturb period"""
    try:
        if is_do_not_disturb_time():
            brightness = int(config.DIM_BRIGHTNESS_PERCENT / 100 * 255)
            print(f"Setting brightness to dim: {config.DIM_BRIGHTNESS_PERCENT}%")
        else:
            brightness = int(config.NORMAL_BRIGHTNESS_PERCENT / 100 * 255)
            print(f"Setting brightness to normal: {config.NORMAL_BRIGHTNESS_PERCENT}%")
        
        M5.Lcd.setBrightness(brightness)
    except Exception as e:
        print("Brightness error:", e)

def get_local_time():
    """Get local time considering the timezone offset"""
    utc_time = time.time()
    local_time = utc_time + config.TIMEZONE_OFFSET_HOURS * 3600
    return time.localtime(local_time)

def is_do_not_disturb_time():
    """Check if the current time is within the do not disturb period"""
    current_hour = get_local_time()[3]
    start = config.DO_NOT_DISTURB_START_HOUR
    end = config.DO_NOT_DISTURB_END_HOUR

    # Handle overnight period
    if start > end:
        return current_hour >= start or current_hour < end
    else:
        return start <= current_hour < end

def initialize_device():
    """Initialize M5Stack Core S3 device"""
    try:
        M5.begin()
        M5.Lcd.clear()
        M5.Speaker.begin()
        print("M5Stack Core S3 initialized")
        return True
    except Exception as e:
        print("Init error:", e)
        return False 