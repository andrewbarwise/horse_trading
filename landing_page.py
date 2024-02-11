from src.betfair import Betfair
import streamlit as st
from src.streamlit_funcs import *

api_key = 'ABGJLOlKaLtTsMIp'
auth_token = 'NYbQ0LYO9CrBhNMiGSSJOTyagPcfbdGsoc8ZgG/0J0M='

# create instance of Betfair class
bf = Betfair(api_key, auth_token)

# check connection
if st.button('Check Betfair connection'):
    bf.check_connection()

# display account balance
balance = bf.account_balance()
st.metric(label = 'Account Balance', value = balance)

# Get current date and set market start time and end time
today_date = datetime.utcnow().date()
start_time = today_date.strftime('%Y-%m-%dT00:00:01Z')
end_time = today_date.strftime('%Y-%m-%dT23:59:59Z')

# Fetch horse racing market data

horse_racing_data = bf.list_market_horse(start_time, end_time)

# Display the fetched data in a Streamlit table
if horse_racing_data is not None:
    st.dataframe(horse_racing_data)
else:
    st.warning('No horse racing data available for the current day.')


# Define market_id based on the specific market you want to retrieve price data for
market_id = '1.224715808'

# Call the get_market_price_data method
price_data = bf.get_market_price_data(market_id)

# Display the price data in Streamlit
st.write("Market Price Data:")
#st.write(price_data)

if price_data is not None:
    st.dataframe(price_data)
else:
    st.warning('No price data available for the current day.')