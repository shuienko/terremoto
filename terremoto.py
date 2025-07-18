#!/usr/bin/env python3
"""
Terremoto - Earthquake monitoring tool
Fetches earthquake data from EMSC API and monitors for earthquakes within a specified radius.
"""

import json
import math
import time
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Set
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError


class Earthquake:
    """Represents an earthquake event"""
    def __init__(self, magnitude: float, latitude: float, longitude: float, 
                 time: datetime, place: str, distance: float = 0.0):
        self.magnitude = magnitude
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
        self.place = place
        self.distance = distance
    
    def get_id(self) -> str:
        """Generate unique identifier for earthquake"""
        return f"{self.magnitude}_{self.latitude}_{self.longitude}_{self.time.isoformat()}"


class EarthquakeMonitor:
    """Earthquake monitoring system"""
    
    def __init__(self):
        # Nerja, Spain coordinates
        self.latitude = 36.7506
        self.longitude = -3.8739
        self.radius_km = 400.0
        self.shown_earthquakes_file = "shown_earthquakes.json"
        
        print(f"Initialized earthquake monitor for Nerja, Spain: {self.latitude:.4f}, {self.longitude:.4f}")
        print(f"Monitoring radius: {self.radius_km:.1f}km")
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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
    
    def load_shown_earthquakes(self) -> Set[str]:
        """Load previously shown earthquake IDs from file"""
        try:
            if os.path.exists(self.shown_earthquakes_file):
                with open(self.shown_earthquakes_file, 'r') as f:
                    return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass
        return set()
    
    def save_shown_earthquakes(self, shown_ids: Set[str]):
        """Save shown earthquake IDs to file"""
        try:
            with open(self.shown_earthquakes_file, 'w') as f:
                json.dump(list(shown_ids), f)
        except IOError:
            pass
    
    def fetch_earthquakes(self) -> Tuple[List[Earthquake], int]:
        """Fetch earthquakes from EMSC API for the last hour"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Build EMSC query URL
        params = {
            'format': 'json',
            'starttime': start_str,
            'endtime': end_str,
            'minmag': '0'
        }
        
        base_url = "https://www.seismicportal.eu/fdsnws/event/1/query"
        url = f"{base_url}?{urlencode(params)}"
        
        try:
            with urlopen(url, timeout=30) as response:
                if response.status != 200:
                    print(f"HTTP error: {response.status}")
                    return [], 0
                data_bytes = response.read()
                data_str = data_bytes.decode('utf-8')
        except (URLError, HTTPError) as e:
            print(f"Error fetching earthquake data: {e}")
            return [], 0
        
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return [], 0
        
        earthquakes = []
        
        if 'features' not in data:
            print("No features found in API response")
            return earthquakes, 0
        
        for feature in data['features']:
            try:
                properties = feature['properties']
                geometry = feature['geometry']
                
                if len(geometry['coordinates']) < 2:
                    continue
                
                longitude = geometry['coordinates'][0]
                latitude = geometry['coordinates'][1]
                magnitude = properties.get('mag', 0.0)
                place = properties.get('flynn_region', 'Unknown location')
                time_str = properties.get('time', '')
                
                # Parse time
                eq_time = datetime.now(timezone.utc)  # default fallback
                if time_str:
                    try:
                        if time_str.endswith('Z'):
                            eq_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        else:
                            eq_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        try:
                            eq_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            pass
                
                # Calculate distance
                distance = self.haversine_distance(
                    self.latitude, self.longitude, latitude, longitude
                )
                
                earthquake = Earthquake(
                    magnitude=magnitude,
                    latitude=latitude,
                    longitude=longitude,
                    time=eq_time,
                    place=place,
                    distance=distance
                )
                earthquakes.append(earthquake)
                
            except (KeyError, ValueError, TypeError) as e:
                continue
        
        total_found = len(earthquakes)
        
        # Filter by radius
        filtered_earthquakes = [eq for eq in earthquakes if eq.distance <= self.radius_km]
        
        return filtered_earthquakes, total_found
    
    def print_earthquake_alert(self, earthquakes: List[Earthquake], total_found: int):
        """Print earthquake alert to stdout"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not earthquakes:
            print(f"[{timestamp}] No earthquakes detected in your area in the last hour. "
                  f"Total earthquakes found worldwide: {total_found}")
            return
        
        print(f"\n[{timestamp}] EARTHQUAKE ALERT!")
        print(f"Location: {self.latitude:.4f}, {self.longitude:.4f}")
        print(f"Radius: {self.radius_km:.1f}km")
        print(f"Found {len(earthquakes)} earthquake(s) in your area (out of {total_found} total worldwide):")
        print("-" * 60)
        
        # Limit to 10 earthquakes for readability
        display_earthquakes = earthquakes[:10]
        
        for i, eq in enumerate(display_earthquakes, 1):
            print(f"{i}. Magnitude {eq.magnitude:.1f} - {eq.place}")
            print(f"   Time: {eq.time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"   Distance: {eq.distance:.1f}km")
            print()
        
        if len(earthquakes) > 10:
            print(f"... and {len(earthquakes) - 10} more earthquakes")
        
        print("-" * 60)
    
    def run(self):
        """Main monitoring loop - checks every 5 minutes"""
        print("Starting earthquake monitoring (checking every 5 minutes for last hour earthquakes)...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                earthquakes, total_found = self.fetch_earthquakes()
                
                # Load previously shown earthquakes
                shown_ids = self.load_shown_earthquakes()
                
                # Filter out already shown earthquakes
                new_earthquakes = [eq for eq in earthquakes if eq.get_id() not in shown_ids]
                
                if new_earthquakes:
                    self.print_earthquake_alert(new_earthquakes, total_found)
                    
                    # Save new earthquake IDs as shown
                    new_ids = {eq.get_id() for eq in new_earthquakes}
                    shown_ids.update(new_ids)
                    self.save_shown_earthquakes(shown_ids)
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if earthquakes:
                        print(f"[{timestamp}] No new earthquakes in radius. Total worldwide: {total_found}")
                    else:
                        print(f"[{timestamp}] No earthquakes in radius. Total worldwide: {total_found}")
                
                # Wait 5 minutes
                time.sleep(300)
                
        except KeyboardInterrupt:
            print("\nStopping earthquake monitoring...")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")


def main():
    """Main entry point"""
    try:
        monitor = EarthquakeMonitor()
        monitor.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()