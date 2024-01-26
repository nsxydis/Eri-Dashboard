'''
Purpose: Main page for the dashboard.

Author: Nick Xydis

Version 1.0 - Programmer: Nick Xydis
26Jan2024   - Created.
'''

import streamlit as st
import polars as pl
import altair as alt

def main():
    upload = st.file_uploader("Upload a file")

    # If we have a file, display it
    if upload is not None:
        df = pl.read_csv(upload, infer_schema_length=None)

        st.write("# Uploaded Dataframe")
        st.dataframe(df)

    # Example chart
    dfDemo = pl.read_csv('demo.csv')
    chart = alt.Chart(dfDemo.to_pandas()).mark_line().encode(
            x = 'a',
            y = 'c'
        )
    st.write("# Chart Demonstration")
    st.altair_chart(chart)

if __name__ == "__main__":
    main()