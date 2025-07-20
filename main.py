"""
Terremoto - M5Stack Core S3 earthquake monitor
MicroPython version for Core S3
"""

import time
import gc

from config import (
    CHECK_INTERVAL_MINUTES,
    ERROR_MESSAGE_MAX_LENGTH,
)
from display import (
    display_info,
    display_success,
    display_warning,
    display_error,
    display_earthquake_alert,
    MESSAGES,
    show_startup_message,
    format_earthquake_message
)
from api import fetch_earthquakes
from utils import format_time
from device import initialize_device, play_tone_alert, set_display_brightness
from network_utils import connect_wifi, sync_time_with_ntp, ensure_wifi_connection

def monitoring_loop():
    """Main monitoring loop"""
    last_earthquake_unid = None
    while True:
        try:
            # Set brightness
            set_display_brightness()

            # Ensure WiFi connection
            if not ensure_wifi_connection():
                continue
            
            # Fetch earthquake data
            earthquakes, total_found = fetch_earthquakes()
            check_timestamp = format_time()
            
            earthquake_to_display = None
            
            # Decide whether to alert for an earthquake
            if earthquakes:
                strongest = max(earthquakes, key=lambda eq: eq['magnitude'])

                # Play tone alert if the earthquake is new
                if strongest['unid'] != last_earthquake_unid:
                    play_tone_alert(strongest['magnitude'])
                
                last_earthquake_unid = strongest['unid']
                earthquake_to_display = strongest
            else:
                last_earthquake_unid = None  # Reset when no earthquakes are in range
            
            # Format and display message
            message, message_type = format_earthquake_message(earthquake_to_display, total_found, check_timestamp)
            
            if message_type == "alert":
                display_earthquake_alert(message)
            elif message_type == "success":
                display_success(message)
            elif message_type == "warning":
                display_warning(message)
            else:
                display_info(message)
            
            # Clean up memory
            gc.collect()
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
            
        except KeyboardInterrupt:
            display_info(MESSAGES["STOPPING"])
            break
        except Exception as e:
            error_message = str(e)[:ERROR_MESSAGE_MAX_LENGTH]
            print("Runtime error:", error_message)
            display_error(MESSAGES["RUNTIME_ERROR"].format(error_message))
            time.sleep(60) # Wait for 1 minute before restarting loop
            continue # Restart the loop to recover

def main():
    """Main function - orchestrates the earthquake monitoring system"""
    # Initialize device
    if not initialize_device():
        return
    
    # Set initial brightness
    set_display_brightness()
    
    # Show startup message
    show_startup_message()
    
    # Initial WiFi connection
    wifi_connected = connect_wifi()

    # If the first attempt fails, show a message, wait, and retry once more before giving up.
    if not wifi_connected:
        display_error(MESSAGES["WIFI_FAILED"].format(CHECK_INTERVAL_MINUTES))
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        wifi_connected = connect_wifi()

    if wifi_connected:
        sync_time_with_ntp()
    else:
        # Abort startup if we still have no network; avoids crashing later.
        print("Startup aborted: unable to establish WiFi connection.")
        display_error(MESSAGES["WIFI_FAILED"].format(CHECK_INTERVAL_MINUTES))
        return
    
    # Start monitoring loop
    monitoring_loop()

# Run the main function
if __name__ == "__main__":
    main()