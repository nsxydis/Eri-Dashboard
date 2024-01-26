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
    st.write(ss)

    # Option initializaton
    init = {
        'numCharts' : 1
    }

    # Initialize the options
    for item in init:
        if item not in ss:
            ss[item] = init[item]

    # Page options
    with st.sidebar:
        # Number of graphs -- TODO: Default to 1 for now
        # st.number_input("Number of Charts", value = ss.numCharts, min_value = 1, step = 1, key = 'numCharts')
        ss.numCharts = 1

        # Chart Options
        for n in range(ss.numCharts):
            st.write("# Filter Options")
            st.multiselect("Fields", options = ss.df.columns, key = f'fields{n}')

            # For each field, give options to filter by
            for i in range(len(ss[f"fields{n}"])):
                item = ss[f'fields{n}']
                st.write(f"Filter {item}")
                st.multiselect(item, options = ss.df[item].unique().to_list(), key = f'field{n}Filter{i}')


if __name__ == '__main__':
    main()