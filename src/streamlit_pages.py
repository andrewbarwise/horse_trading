import pytz
from datetime import datetime, timedelta
import streamlit_pages as st
from streamlit_funcs import *
from streamlit.hashing import _CodeHasher

class SessionState:
    def __init__(self, **kwargs):
        # generate a unique key based on the provided kwargs
        key = _CodeHasher()(*kwargs.values())
        # store the session state in streamlits internal state
        self._state = st._get_state(key = key, **kwargs)

# hard code some dummy values, temp measure
valid_username = 'andrew'
valid_password = 'password'

def login(username, password):
    return username == valid_username and password == valid_password

def login_page():
    st.title('Login Page')

    # get or create a SessionState object
    session_state = SessionState(logged_in = False)

    # collect user inputs
    username = st.text_input('Username')
    password = st.text_input('Password', type = 'password')

    # check if login button clicked
    if st.button('Login'):
        if login(username, password):
            session_state.logged_in=True
            st.success('Login Successful')

            #### ADD REDIRECTION LOGIC HERE
        
        else:
            st.error('Invalid credentials. Please try again.')

def page_one():
    from src.betfair import Betfair

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
