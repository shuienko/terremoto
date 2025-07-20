import M5
import time
import config

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

def play_tone_alert(magnitude):
    """Play a tone alert based on earthquake magnitude"""
    try:
        if is_do_not_disturb_time() and magnitude < 5.0:
            print("In 'do not disturb' period. Alert silenced.")
            return

        if 1.0 <= magnitude < 2.0:
            num_signals = 1
            duration = 100  # Short beep
        elif 2.0 <= magnitude < 3.0:
            num_signals = 2
            duration = 100  # Short beeps
        elif 3.0 <= magnitude < 4.0:
            num_signals = 3
            duration = 100  # Short beeps
        elif 4.0 <= magnitude < 5.0:
            num_signals = 4
            duration = 300  # Medium beeps
        elif 5.0 <= magnitude < 6.0:
            num_signals = 5
            duration = 500  # Long beeps
        elif magnitude >= 6.0:
            num_signals = 10
            duration = 500  # Long beeps
        else:
            return  # No sound for magnitudes below 1.0

        frequency = 1000
        for i in range(num_signals):
            M5.Speaker.tone(frequency, duration)
            if i < num_signals - 1:
                time.sleep(0.8)
    except Exception as e:
        print("Speaker error:", e) 