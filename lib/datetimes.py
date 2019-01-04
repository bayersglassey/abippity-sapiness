
import pytz
from datetime import datetime
from tzlocal import get_localzone

def get_local_now():
    local_tz = get_localzone()
    utc_now = datetime.utcnow()
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_now
