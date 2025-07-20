"""
Terremoto - M5Stack Core S3 earthquake monitor
MicroPython version for Core S3
"""

import time
import math
import gc
import requests
import M5
import network
import ntptime

# Import configuration
try:
    from config import (
        WIFI_SSID, WIFI_PASSWORD, MONITOR_LATITUDE, MONITOR_LONGITUDE, 
        TIMEZONE_OFFSET_HOURS, MONITOR_RADIUS_KM, CHECK_INTERVAL_MINUTES,
        API_QUERY_PERIOD_MINUTES,
        FONT, LINE_HEIGHT, MAX_LINES,
        WIFI_MAX_RETRIES, WIFI_RETRY_DELAY, WIFI_MAX_WAIT, HTTP_TIMEOUT,
        EMSC_BASE_URL, MIN_MAGNITUDE, EARTH_RADIUS_KM,
        PLACE_NAME_MAX_LENGTH, ERROR_MESSAGE_MAX_LENGTH, STARTUP_DISPLAY_DELAY
    )
except ImportError:
    print("Error: config.py not found. Please create config.py from config.template.py")
    raise

# -- Message Formats --
MESSAGES = {
    "STARTUP": "EARTHQUAKE MONITOR\n\nStarting...\n\nLat: {:.2f}\nLon: {:.2f}\nRadius: {}km",
    "WIFI_LOST": "WIFI LOST\n\nReconnecting...",
    "WIFI_FAILED": "WIFI FAILED\n\nRetrying in\n{} minutes",
    "SYNCING_TIME": "SYNCING TIME\n\nwith NTP...",
    "TIME_SYNCED": "TIME SYNCED\n\n{}",
    "NTP_FAILED": "NTP FAILED\n\nWill use\nlast known time",
    "CONNECTION_ERROR": "CONNECTION\nERROR\n\nRetrying WiFi\n\nLast check: {}",
    "ALL_CLEAR": "== ALL CLEAR ==\n\nNo earthquakes\nin {}km radius\n\nTotal in the world: {}\nLast check: {}",
    "EARTHQUAKE": "!!! EARTHQUAKE !!!\n\nMag: {:.1f}\n{}\nDist: {:.0f}km\n\nLast check: {}",
    "STOPPING": "STOPPING\n\nMonitor halted",
    "RUNTIME_ERROR": "RUNTIME ERROR\n\n{}\n\nRestarting loop...",
}

def display_text(text):
    """Display text on M5Stack Core S3 screen with larger font and centered text"""
    print("Display:", text)
    
    try:
        M5.Lcd.clear()
        
        # Set font from config
        M5.Lcd.setFont(getattr(M5.Lcd.FONTS, FONT))
        
        # Get screen dimensions
        screen_width = M5.Display.width()
        screen_height = M5.Display.height()
        
        lines = text.split('\n')
        max_lines = MAX_LINES
        
        # Calculate total text height
        line_height = LINE_HEIGHT
        total_text_height = min(len(lines), max_lines) * line_height
        
        # Start y position to center text vertically
        start_y = (screen_height - total_text_height) // 2
        
        y = start_y
        for line in lines[:max_lines]:
            if line.strip():  # Only process non-empty lines
                # Calculate x position to center text horizontally
                # Use M5Stack's textWidth method for accurate centering
                try:
                    text_width = M5.Lcd.textWidth(line)
                    x = max(0, (screen_width - text_width) // 2)
                except:
                    # Fallback to manual calculation if textWidth not available
                    text_width = len(line) * 10
                    x = max(0, (screen_width - text_width) // 2)
                
                M5.Lcd.drawString(line, x, y)
            y += line_height
            
    except Exception as e:
        print("LCD Error:", e)

def connect_wifi(max_retries=WIFI_MAX_RETRIES, retry_delay=WIFI_RETRY_DELAY):
    """Connect to WiFi network with retry logic"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi")
        return True
    
    for attempt in range(max_retries):
        print("Connecting to WiFi (attempt {}/{})...".format(attempt + 1, max_retries))
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection
        max_wait = WIFI_MAX_WAIT
        while max_wait > 0:
            if wlan.isconnected():
                print("Connected to WiFi")
                print("IP:", wlan.ifconfig()[0])
                return True
            max_wait -= 1
            time.sleep(1)
        
        print("Failed to connect to WiFi (attempt {}/{})".format(attempt + 1, max_retries))
        
        # If not last attempt, wait before retrying
        if attempt < max_retries - 1:
            print("Retrying in {} seconds...".format(retry_delay))
            time.sleep(retry_delay)
    
    print("Failed to connect to WiFi after {} attempts".format(max_retries))
    return False

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    earth_radius = EARTH_RADIUS_KM
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    return c * earth_radius

def build_api_url():
    """Build EMSC API URL with time parameters"""
    current_time = time.time()
    start_time = current_time - (API_QUERY_PERIOD_MINUTES * 60)
    
    start_tuple = time.localtime(start_time)
    start_iso = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        start_tuple[0], start_tuple[1], start_tuple[2],
        start_tuple[3], start_tuple[4], start_tuple[5]
    )
    
    params = "?format=json&minmag={}&starttime={}".format(MIN_MAGNITUDE, start_iso)
    return EMSC_BASE_URL + params

def fetch_api_data(url):
    """Make HTTP request to EMSC API and return JSON data"""
    print("Fetching:", url)
    response = requests.get(url, timeout=HTTP_TIMEOUT)
    
    if response.status_code != 200:
        print("HTTP error:", response.status_code)
        response.close()
        return None
    
    data = response.json()
    response.close()
    return data

def parse_earthquake_feature(feature):
    """Parse a single earthquake feature from EMSC API response"""
    properties = feature['properties']
    geometry = feature['geometry']
    
    if len(geometry['coordinates']) < 2:
        return None
    
    unid = properties.get('unid', '')
    longitude = geometry['coordinates'][0]
    latitude = geometry['coordinates'][1]
    magnitude = properties.get('mag', 0.0)
    place = properties.get('flynn_region', 'Unknown')
    timestamp = properties.get('time', 0)
    
    distance = haversine_distance(
        MONITOR_LATITUDE, MONITOR_LONGITUDE, latitude, longitude
    )
    
    if distance <= MONITOR_RADIUS_KM:
        return {
            'unid': unid,
            'magnitude': magnitude,
            'place': place,
            'distance': distance,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp
        }
    
    return None

def parse_earthquakes_data(data):
    """Parse earthquake data from EMSC API response"""
    earthquakes = []
    total_found = 0
    
    if 'features' in data:
        total_found = len(data['features'])
        
        for feature in data['features']:
            try:
                earthquake = parse_earthquake_feature(feature)
                if earthquake:
                    earthquakes.append(earthquake)
            except Exception as e:
                print("Parse error:", e)
                continue
    
    return earthquakes, total_found

def fetch_earthquakes():
    """Fetch earthquake data from EMSC API"""
    try:
        url = build_api_url()
        data = fetch_api_data(url)
        
        if data is None:
            return [], 0
        
        return parse_earthquakes_data(data)
        
    except Exception as e:
        print("Fetch error:", e)
        return [], -1

def format_time():
    """Get current time as string with local timezone"""
    # Get UTC time and adjust for local timezone
    utc_time = time.time()
    local_time = utc_time + (TIMEZONE_OFFSET_HOURS * 3600)
    t = time.gmtime(local_time)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

def sync_time_with_ntp():
    """Synchronize device time with NTP server"""
    print("Synchronizing time with NTP server...")
    display_text(MESSAGES["SYNCING_TIME"])
    try:
        ntptime.settime()
        print("Time synchronized successfully")
        current_time_str = format_time()
        display_text(MESSAGES["TIME_SYNCED"].format(current_time_str))
        time.sleep(2)
        return True
    except Exception as e:
        print("NTP Error:", e)
        display_text(MESSAGES["NTP_FAILED"])
        time.sleep(2)
        return False

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

def show_startup_message():
    """Display startup message with monitoring configuration"""
    startup_msg = MESSAGES["STARTUP"].format(
        MONITOR_LATITUDE, MONITOR_LONGITUDE, MONITOR_RADIUS_KM
    )
    display_text(startup_msg)
    time.sleep(STARTUP_DISPLAY_DELAY)

def ensure_wifi_connection():
    """Ensure WiFi is connected, attempt reconnection if needed"""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("WiFi disconnected, attempting to reconnect...")
        display_text(MESSAGES["WIFI_LOST"])
        wifi_connected = connect_wifi()
        if not wifi_connected:
            display_text(MESSAGES["WIFI_FAILED"].format(CHECK_INTERVAL_MINUTES))
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
            return False
        # If reconnected, sync time
        sync_time_with_ntp()
    return True

def format_earthquake_message(earthquake, total_found, timestamp):
    """Format message based on earthquake data"""
    if total_found == -1:
        return MESSAGES["CONNECTION_ERROR"].format(timestamp)
    elif not earthquake:
        return MESSAGES["ALL_CLEAR"].format(
            MONITOR_RADIUS_KM, total_found, timestamp
        )
    else:
        # Show the provided earthquake
        place_short = earthquake['place'][:PLACE_NAME_MAX_LENGTH]
        return MESSAGES["EARTHQUAKE"].format(
            earthquake['magnitude'], 
            place_short, 
            earthquake['distance'],
            timestamp
        )

def play_tone_alert(frequency=1000, duration=100, num_signals=1):
    """Play a tone alert with specified frequency, duration and repetitions"""
    try:
        for i in range(num_signals):
            M5.Speaker.tone(frequency, duration)
            if i < num_signals - 1:
                time.sleep(0.05)  # 50ms pause between beeps
    except Exception as e:
        print("Speaker error:", e)

def monitoring_loop():
    """Main monitoring loop"""
    last_earthquake_unid = None
    try:
        while True:
            # Ensure WiFi connection
            if not ensure_wifi_connection():
                continue
            
            # Fetch earthquake data
            earthquakes, total_found = fetch_earthquakes()
            timestamp = format_time()
            
            earthquake_to_display = None
            
            # Decide whether to alert for an earthquake
            if earthquakes:
                strongest = max(earthquakes, key=lambda eq: eq['magnitude'])
                if strongest['unid'] != last_earthquake_unid:
                    play_tone_alert()
                    last_earthquake_unid = strongest['unid']
                    earthquake_to_display = strongest
                # If same earthquake, earthquake_to_display remains None, showing ALL CLEAR
            else:
                last_earthquake_unid = None  # Reset when no earthquakes are in range
            
            # Format and display message
            message = format_earthquake_message(earthquake_to_display, total_found, timestamp)
            display_text(message)
            
            # Clean up memory
            gc.collect()
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
            
    except KeyboardInterrupt:
        display_text(MESSAGES["STOPPING"])
    except Exception as e:
        error_message = str(e)[:ERROR_MESSAGE_MAX_LENGTH]
        print("Runtime error:", error_message)
        display_text(MESSAGES["RUNTIME_ERROR"].format(error_message))
        time.sleep(60) # Wait for 1 minute before restarting loop
        monitoring_loop() # Restart the loop to recover

def main():
    """Main function - orchestrates the earthquake monitoring system"""
    # Initialize device
    if not initialize_device():
        return
    
    # Show startup message
    show_startup_message()
    
    # Initial WiFi connection
    wifi_connected = connect_wifi()
    if wifi_connected:
        sync_time_with_ntp()
    
    # Start monitoring loop
    monitoring_loop()

# Run the main function
if __name__ == "__main__":
    main()