import streamlit as st
import polars as pl
import altair as alt

def main():
    # Wait until there is data to display
    if not st.session_state.upload:
        return
    
    # Read in the data

if __name__ == '__main__':
    main()