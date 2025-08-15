"""
Simple Clock - M5Stack Core S3
MicroPython version for Core S3
"""

import time
import gc

from config import (
    TIMEZONE_OFFSET_HOURS,
    UPDATE_INTERVAL_SECONDS,
)
from display import (
    display_clock,
    show_startup_message,
)
from utils import format_time
from device import initialize_device, set_display_brightness
from network_utils import connect_wifi, sync_time_with_ntp, ensure_wifi_connection

def clock_loop():
    """Main clock loop"""
    while True:
        try:
            # Set brightness
            set_display_brightness()

            # Ensure WiFi connection for time sync
            if not ensure_wifi_connection():
                # If no WiFi, just show time without sync
                pass
            
            # Get current time
            current_time = format_time()
            
            # Display clock
            display_clock(current_time)
            
            # Clean up memory
            gc.collect()
            
            # Wait for next update
            time.sleep(UPDATE_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("Stopping clock...")
            break
        except Exception as e:
            print("Runtime error:", str(e))
            time.sleep(10)  # Wait before restarting loop
            continue

def main():
    """Main function - orchestrates the clock system"""
    # Initialize device
    if not initialize_device():
        return
    
    # Set initial brightness
    set_display_brightness()
    
    # Show startup message
    show_startup_message()
    
    # Initial WiFi connection for time sync
    wifi_connected = connect_wifi()

    if wifi_connected:
        sync_time_with_ntp()
    else:
        print("No WiFi connection - clock will run without time sync")
    
    # Start clock loop
    clock_loop()

# Run the main function
if __name__ == "__main__":
    main()