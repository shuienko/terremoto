import M5
import time

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

def play_tone_alert(frequency=1000, duration=100, num_signals=1):
    """Play a tone alert with specified frequency, duration and repetitions"""
    try:
        for i in range(num_signals):
            M5.Speaker.tone(frequency, duration)
            if i < num_signals - 1:
                time.sleep(0.05)  # 50ms pause between beeps
    except Exception as e:
        print("Speaker error:", e) 