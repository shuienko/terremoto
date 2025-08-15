import network
import time
import ntptime

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    WIFI_MAX_RETRIES,
    WIFI_RETRY_DELAY,
    WIFI_MAX_WAIT,
)

from utils import format_time

def connect_wifi(max_retries=WIFI_MAX_RETRIES, retry_delay=WIFI_RETRY_DELAY):
    """Connect to WiFi network with retry logic"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
 
    if wlan.isconnected():
        print("Already connected to WiFi")
        return True
 
    # Resolve status constants with graceful fallback for firmware that omits them
    STAT_GOT_IP = getattr(network, "STAT_GOT_IP", 3)

    for attempt in range(max_retries):
        print("Connecting to WiFi (attempt {}/{})...".format(attempt + 1, max_retries))

        # Ensure any previous connection attempt is stopped
        try:
            wlan.disconnect()
        except Exception:
            pass

        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        start_time = time.time()
        while (time.time() - start_time) < WIFI_MAX_WAIT:
            status = wlan.status()

            if status == STAT_GOT_IP and wlan.isconnected():
                print("Connected to WiFi")
                print("IP:", wlan.ifconfig()[0])
                return True

            # Handle fatal failure codes quickly
            if isinstance(status, int) and status < 0:
                print("WiFi connection failed with status {}".format(status))
                break  # go to next retry

            time.sleep(0.5)  # poll twice per second for snappier feedback
 
        print("Failed to connect to WiFi (attempt {}/{})".format(attempt + 1, max_retries))
 
        # If not last attempt, wait before retrying
        if attempt < max_retries - 1:
            print("Retrying in {} seconds...".format(retry_delay))
            time.sleep(retry_delay)
 
    print("Failed to connect to WiFi after {} attempts".format(max_retries))
    return False

def sync_time_with_ntp():
    """Synchronize device time with NTP server"""
    print("Synchronizing time with NTP server...")
    try:
        ntptime.settime()
        print("Time synchronized successfully")
        current_time_str = format_time()
        print(f"Time synced: {current_time_str}")
        time.sleep(2)
        return True
    except Exception as e:
        print("NTP Error:", e)
        print("Will use last known time")
        time.sleep(2)
        return False

def ensure_wifi_connection():
    """Ensure WiFi is connected, attempt reconnection if needed"""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("WiFi disconnected, attempting to reconnect...")
        print("WiFi lost - reconnecting...")
        wifi_connected = connect_wifi()
        if not wifi_connected:
            print("WiFi reconnection failed")
            return False
        # If reconnected, sync time
        sync_time_with_ntp()
    return True 