'''
Purpose: Main page for the dashboard.

Author: Nick Xydis

Version 1.0 - Programmer: Nick Xydis
26Jan2024   - Created.
'''

import streamlit as st
import polars as pl
import altair as alt
import os

def main():
    # Debugging...
    # st.write(st.session_state)

    # Initialize failure
    if 'failure' not in st.session_state:
        st.session_state.failure = False
    
    # Upload a file
    st.file_uploader("Upload a file", key = 'upload')

    if st.session_state.upload and not st.session_state.failure:
        # Try to read in the data
        try:
            df = pl.read_csv(st.session_state.upload)
            st.session_state.df = df
            st.write("File read in succesfully!")
        except:
            st.session_state.failure = True
            st.write("Could not read uploaded file!")
            st.write("Please refresh the page and try again.")

    # How to use this app details below...
            
    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        st.session_state[k] = v

if __name__ == "__main__":
    main()