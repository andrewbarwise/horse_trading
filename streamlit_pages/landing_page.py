from src.betfair import Betfair
import streamlit as st
from src.streamlit_funcs import *

api_key = 'ABGJLOlKaLtTsMIp'
auth_token = 'SWahjOHWwjsxOEg+u232YS5eLrnFA8pDeM8J1LTAl70='

# create instance of Betfair class
bf = Betfair(api_key, auth_token)

# check connection
if st.button('Check Betfair connection'):
    bf.check_connection()

# display account balance
balance = bf.account_balance()
st.metric(label = 'Account Balance', value = balance)

dates = date_list()

# create a date dropdown box
selected_date = st.selectbox('Select a date', date_list())

start_time, end_time = format_selected_date(selected_date)

# check if valid dates are returned
if start_time and end_time:
    bf.list_market_horse(start_time, end_time)
else:
    st.error('Invalid date selected')