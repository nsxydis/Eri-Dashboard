import streamlit as st
import polars as pl
import altair as alt
import pageHelper as ph

def main():
    # Page initialization, stop on error
    if ph.init() != 0:
        return

    # 
    # st.write(st.session_state)
    
    # Read in the data

if __name__ == '__main__':
    main()