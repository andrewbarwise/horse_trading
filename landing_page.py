import streamlit as st 
from src.streamlit import *

st.write('Hello')

selected_date = st.selectbox('Select a date', date_list())