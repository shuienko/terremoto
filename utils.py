import time
from config import TIMEZONE_OFFSET_HOURS

def format_time():
    """Get current time as string with local timezone"""
    # Get UTC time and adjust for local timezone
    utc_time = time.time()
    local_time = utc_time + (TIMEZONE_OFFSET_HOURS * 3600)
    t = time.gmtime(local_time)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

def format_event_time(iso_timestamp):
    """
    Get earthquake event time as a string with local timezone from an ISO timestamp.
    Example input: "2024-07-20T10:32:17.110Z"
    """
    if not iso_timestamp or 'T' not in iso_timestamp:
        return "Unknown"
    
    try:
        # 1. Parse ISO string to get date and time components
        # e.g., "2024-07-20T10:32:17.110Z"
        date_part, time_part_full = iso_timestamp.split('T')
        
        # "2024-07-20" -> (2024, 7, 20)
        year, month, day = [int(p) for p in date_part.split('-')]
        
        # "10:32:17.110Z" -> "10:32:17" -> (10, 32, 17)
        time_part = time_part_full.split('.')[0]
        h, m, s = [int(p) for p in time_part.split(':')]

        # 2. Create a time tuple for MicroPython's time.mktime.
        # It requires a 9-tuple: (year, month, mday, hour, minute, second, weekday, yearday, isdst)
        # Weekday, yearday, and isdst can be dummy values.
        event_utc_tuple = (year, month, day, h, m, s, 0, 0, 0)

        # 3. Convert the UTC tuple to seconds since the epoch.
        # On a system where the clock is UTC (set by NTP), mktime treats the tuple as UTC.
        event_utc_seconds = time.mktime(event_utc_tuple)
        
        # 4. Apply the timezone offset to get local time in seconds.
        event_local_seconds = event_utc_seconds + (TIMEZONE_OFFSET_HOURS * 3600)
        
        # 5. Convert local time in seconds back to a time tuple.
        # Use time.gmtime() to format seconds into a tuple without extra timezone conversion.
        t = time.gmtime(event_local_seconds)
        
        # 6. Format the time part.
        return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

    except (ValueError, IndexError) as e:
        print("Time parse error:", e)
        # Fallback for unexpected timestamp format
        try:
            time_part = iso_timestamp.split('T')[1].split('.')[0]
            return f"{time_part} UTC"
        except Exception:
            return "Invalid Time" 