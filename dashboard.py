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
    # Initialize
    st.session_state.upload = None
    st.session_state.failure = None

    # Upload a file
    st.session_state.upload = st.file_uploader("Upload a file")

    if st.session_state.upload and not st.session_state.failure:
        # Try to read in the data
        try:
            df = pl.read_csv(st.session_state.upload)
        except:
            st.session_state.failure = True
            st.write("Could not read uploaded file!")
            st.write("Please refresh the page and try again.")

    # How to use this app details below...

if __name__ == "__main__":
    main()