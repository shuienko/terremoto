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

print("M5Stack Core S3 libraries loaded")

# Import configuration
try:
    from config import WIFI_SSID, WIFI_PASSWORD, MONITOR_LATITUDE, MONITOR_LONGITUDE, TIMEZONE_OFFSET_HOURS, MONITOR_RADIUS_KM, CHECK_INTERVAL_MINUTES
except ImportError:
    print("Error: config.py not found. Please create config.py from config.template.py")
    raise

def display_text(text):
    """Display text on M5Stack Core S3 screen with larger font and centered text"""
    print("Display:", text)
    
    try:
        M5.Lcd.clear()
        
        # Set larger font size
        M5.Lcd.setTextSize(2)
        
        # Get screen dimensions (M5Stack Core S3: 320x240)
        screen_width = 320
        screen_height = 240
        
        lines = text.split('\n')
        max_lines = 8  # Reduced for larger font
        
        # Calculate total text height
        line_height = 25  # Increased for larger font
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

def connect_wifi(max_retries=3, retry_delay=5):
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
        max_wait = 10
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
    earth_radius = 6371  # Earth's radius in kilometers
    
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

def fetch_earthquakes():
    """Fetch earthquake data from EMSC API"""
    try:
        # Get current time (simplified - no timezone handling in MicroPython)
        # Using seconds since epoch approximation
        current_time = time.time()
        start_time = current_time - (CHECK_INTERVAL_MINUTES * 60)
        
        # Convert timestamps to ISO format for API
        # EMSC API expects format: YYYY-MM-DDTHH:MM:SS
        start_tuple = time.localtime(start_time)
        start_iso = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            start_tuple[0], start_tuple[1], start_tuple[2],
            start_tuple[3], start_tuple[4], start_tuple[5]
        )
        
        base_url = "https://www.seismicportal.eu/fdsnws/event/1/query"
        params = "?format=json&minmag=0&starttime={}".format(start_iso)
        
        url = base_url + params
        print("Fetching:", url)
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print("HTTP error:", response.status_code)
            response.close()
            return [], 0
        
        data = response.json()
        response.close()
        
        earthquakes = []
        total_found = 0
        
        if 'features' in data:
            total_found = len(data['features'])
            
            for feature in data['features']:
                try:
                    properties = feature['properties']
                    geometry = feature['geometry']
                    
                    if len(geometry['coordinates']) < 2:
                        continue
                    
                    longitude = geometry['coordinates'][0]
                    latitude = geometry['coordinates'][1]
                    magnitude = properties.get('mag', 0.0)
                    place = properties.get('flynn_region', 'Unknown')
                    timestamp = properties.get('time', 0)  # Get earthquake timestamp
                    
                    # Calculate distance
                    distance = haversine_distance(
                        MONITOR_LATITUDE, MONITOR_LONGITUDE, latitude, longitude
                    )
                    
                    # Only include earthquakes within radius
                    if distance <= MONITOR_RADIUS_KM:
                        earthquakes.append({
                            'magnitude': magnitude,
                            'place': place,
                            'distance': distance,
                            'latitude': latitude,
                            'longitude': longitude,
                            'timestamp': timestamp
                        })
                        
                except Exception as e:
                    print("Parse error:", e)
                    continue
        
        return earthquakes, total_found
        
    except Exception as e:
        print("Fetch error:", e)
        return [], -1

def format_time():
    """Get current time as string with Spain timezone"""
    # Get UTC time and adjust for Spain timezone
    utc_time = time.time()
    spain_time = utc_time + (TIMEZONE_OFFSET_HOURS * 3600)
    t = time.gmtime(spain_time)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

def main():
    """Main function"""
    # Initialize display
    try:
        M5.begin()
        M5.Lcd.clear()
        print("M5Stack Core S3 initialized")
    except Exception as e:
        print("Init error:", e)
    
    # Show startup message
    display_text("TERREMOTO MONITOR\n\nStarting\n\nLat: {:.2f}\nLon: {:.2f}\nRadius: {}km".format(MONITOR_LATITUDE, MONITOR_LONGITUDE, MONITOR_RADIUS_KM))
    time.sleep(3)
    
    # Connect to WiFi
    wifi_connected = connect_wifi()
    if not wifi_connected:
        display_text("WIFI FAILED\n\nWill retry\nduring operation")
    
    try:
        while True:
            # Check WiFi connection before fetching data
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("WiFi disconnected, attempting to reconnect...")
                display_text("WIFI LOST\n\nReconnecting...")
                wifi_connected = connect_wifi()
                if not wifi_connected:
                    display_text("WIFI FAILED\n\nRetrying in\n{} minutes".format(CHECK_INTERVAL_MINUTES))
                    time.sleep(CHECK_INTERVAL_MINUTES * 60)
                    continue
            
            # Fetch earthquake data
            earthquakes, total_found = fetch_earthquakes()
            timestamp = format_time()
            
            if total_found == -1:
                message = "CONNECTION\nERROR\n\nRetrying WiFi\n\nLast check: {}".format(timestamp)
                # Try to reconnect WiFi on connection error
                connect_wifi()
            elif not earthquakes:
                message = "ALL CLEAR\n\nNo earthquakes\nin {}km radius\n\nTotal: {}\nLast check: {}".format(MONITOR_RADIUS_KM, total_found, timestamp)
            else:
                # Show biggest earthquake if more than one happened
                strongest = max(earthquakes, key=lambda eq: eq['magnitude'])
                place_short = strongest['place'][:15]
                message = "EARTHQUAKE!\n\nMag: {:.1f}\n{}\nDist: {:.0f}km\n\nLast check: {}".format(
                        strongest['magnitude'], 
                        place_short, 
                        strongest['distance'],
                        timestamp
                )
            
            display_text(message)
            
            # Clean up memory
            gc.collect()
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
            
    except KeyboardInterrupt:
        display_text("STOPPING\n\nMonitor halted")
    except Exception as e:
        display_text("ERROR\n\n{}".format(str(e)[:30]))

# Run the main function
if __name__ == "__main__":
    main()