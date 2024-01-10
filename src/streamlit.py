import pytz
from datetime import datetime, timedelta

def date_list():
    tz = pytz.timezone('UTC')
    start_times = []
    end_times = []

    for ii in range(3):
        start_time = datetime.utcnow() + timedelta(days = ii)
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = tz.localize(start_time).strftime('%Y-%m-%dT%H:%M:%SZ')

        end_time = start_time[:-1] + '23:59:59Z'

        start_times.append(start_time)
        end_times.append(end_time)

    return start_times, end_times