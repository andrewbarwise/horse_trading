import pytz
from datetime import datetime, timedelta

def date_list():
    tz = pytz.timezone('UTC')
    date_list = [(datetime.today() + timedelta(days=i)) \
                 .replace(tzinfo=tz).strftime('%Y-%m-%dT%H:%M:%SZ') for i in range(3)]
    
    return date_list