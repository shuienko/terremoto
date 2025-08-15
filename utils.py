import time
from config import TIMEZONE_OFFSET_HOURS

def format_time():
    """Get current time as string with local timezone in HH:MM format"""
    # Get UTC time and adjust for local timezone
    utc_time = time.time()
    local_time = utc_time + (TIMEZONE_OFFSET_HOURS * 3600)
    t = time.gmtime(local_time)
    return "{:02d}:{:02d}".format(t[3], t[4]) 