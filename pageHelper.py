import streamlit as st

def init():
    '''Default start for all pages'''
    # If we haven't used the dashboard page yet...
    if 'upload' not in st.session_state:
        st.write("Go back to the dashboard page!")
        return 1

    # If there isn't a file uploaded yet...
    elif st.session_state.upload == None and 'df' not in st.session_state:
        st.write("You'll need to upload a csv file to continue!")
        return 2

    # If a file was uploaded and couldn't be read in...
    if 'failure' in st.session_state and st.session_state.failure == True:
        st.write("The file upload failed. Please go back to the dashboard page and try again!")
        st.write("If the failure persists, make sure you're uploading a csv file.")
        return 3
    
    # If there are no failures...
    return 0