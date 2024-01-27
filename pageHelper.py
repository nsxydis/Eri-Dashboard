import streamlit as st

def init():
    '''Default start for all pages'''
    # If we haven't used the dashboard page yet...
    if 'df' not in st.session_state:
        st.write("Go back to the dashboard page!")
        st.write("You need to upload a csv file.")
        return 1
    
    # If there are no failures...
    return 0

def ss(variable, value = None):
    '''Checks if a variable is in the session state and sets its value if not'''
    if variable not in st.session_state:
        st.session_state[variable] = value