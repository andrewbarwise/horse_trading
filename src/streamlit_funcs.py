import pytz
from datetime import datetime, timedelta

def date_list():
    tz = pytz.timezone('UTC')
    start_times = []

    for ii in range(3):
        start_time = datetime.utcnow() + timedelta(days = ii)
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        formatted_time = tz.localize(start_time).strftime('%Y-%m-%dT%H:%M:%SZ')

        start_times.append(formatted_time)

    return start_times

def format_selected_date(selected_date):
    date_mapping = {
        '00:00:01': 'T00:00:01Z',
        '23:59:59': 'T23:59:59Z'
    }

    if selected_date in date_mapping:
        current_date = datetime.utcnow().strftime('%Y-%m-%d')
        time_suffix = date_mapping[selected_date]

        formatted_start_time = f"{current_date}T00:00:01Z"
        formatted_end_time = f"{current_date}T23:59:59Z"

        return formatted_start_time, formatted_end_time
    else:
        return None, None