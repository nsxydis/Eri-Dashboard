import streamlit as st
import polars as pl
import altair as alt
import pageHelper as ph

def main():
    # Page initialization, stop on error
    if ph.init() != 0:
        return

    # Shorthand
    ss = st.session_state

    # Debugging...
    # st.write(ss)

    # Option initializaton
    init = {
        'numCharts'         : 1,
        'primaryField'      : None,
        'secondaryField'    : None
    }

    # Initialize the options
    for item in init:
        if item not in ss:
            ss[item] = init[item]

    # Page options
    with st.sidebar:
        # Chart Options
        st.write("# Filter Options")
        st.multiselect("Fields", options = ss.df.columns, key = 'fields')

        # For each field, give options to filter by
        for n in range(len(ss["fields"])):
            item = ss[f'fields'][n]
            st.multiselect(f"Filter {item}", options = ss.df[item].unique().to_list(), key = f'fieldFilter{n}')

        # Field to separate by
        st.selectbox("Primary Breakdown Field", options = ss.df.columns, key = 'primaryField')
            
        # TODO: Secondary Plots

    # Make a copy of the data
    df = ss.df.copy()

    # Start subsetting...
    for n in range(len(ss.fields)):
        field = ss.fields[n]
        df = df.filter(pl.col(field).is_in(ss[f"fieldFilter{n}"]))
    
    # Make the charts
    primary = alt.Chart(df.to_pandas()).mark_arc().encode(
        x = ss.primaryField,
        color = f"{ss.primaryField}:N"
    )

    # Plot
    st.altair_chart(primary)



if __name__ == '__main__':
    main()