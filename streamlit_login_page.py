from src.streamlit_funcs import *
import hashlib
import streamlit as st

class SessionState:
    def __init__(self, **kwargs):
        # generate a unique key based on the provided kwargs
        key = hashlib.sha256(repr(kwargs).encode()).hexdigest()
        # store the session state in streamlit's session_state
        st.session_state[key] = kwargs
        self._key = key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

valid_username = 'andrew'
valid_password_hash = hash_password('password')  

def login(username, password):
    # Check if the username is valid
    if username == valid_username:
        # Hash the entered password for comparison
        entered_password_hash = hash_password(password)
        
        # Compare hashed passwords
        return entered_password_hash == valid_password_hash
    
    return False

def login_page():
    st.title('Login Page')

    # get or create a SessionState object
    session_state = SessionState(logged_in=False)

    # collect user inputs
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    # check if login button clicked
    if st.button('Login'):
        if login(username, password):
            session_state.logged_in = True
            st.success('Login Successful')

            # Redirect to another page
            redirect_path = '/landing_page'  # Adjust the desired path
            st.experimental_set_query_params(login_success=True, redirect=redirect_path)

        else:
            st.error('Invalid credentials. Please try again.')

if __name__ == login_page():
    login_page()