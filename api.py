import time
import math
import requests

from config import (
    API_QUERY_PERIOD_MINUTES,
    MIN_MAGNITUDE,
    EMSC_BASE_URL,
    HTTP_TIMEOUT,
    MONITOR_LATITUDE,
    MONITOR_LONGITUDE,
    MONITOR_RADIUS_KM,
    EARTH_RADIUS_KM
)

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
    timestamp = properties.get('time', '')
    
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