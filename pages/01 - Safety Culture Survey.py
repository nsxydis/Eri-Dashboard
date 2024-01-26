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
        st.multiselect("Filter Fields", options = ss.df.columns, key = 'fields')

        # For each field, give options to filter by
        for n in range(len(ss["fields"])):
            item = ss[f'fields'][n]
            st.multiselect(f"Filter {item}", options = ss.df[item].unique().to_list(), key = f'fieldFilter{n}')

        # Field to separate by
        st.selectbox("Primary Breakdown Field", options = ss.df.columns, key = 'primaryField')
            
        # Secondary Plots
        if ss.primaryField:      
            secondaryColumns = ss.df.columns.copy()
            secondaryColumns.remove(ss.primaryField)
            secondaryColumns = ['None'] + secondaryColumns
            st.selectbox("Secondary Breakdown Field", options = secondaryColumns, key = 'secondaryField')


    # Stop if we don't have a primary field
    if not ss.primaryField:
        st.write("Select a Primary Breakdown Field first")
        return 1

    # Make a copy of the data
    df = ss.df.clone()

    # Start subsetting...
    for n in range(len(ss.fields)):
        # Skip if nothing was selected for a field
        if len(ss[f"fieldFilter{n}"]) == 0:
            continue

        # Otherwise get the field and filter the data
        field = ss.fields[n]
        df = df.filter(pl.col(field).is_in(ss[f"fieldFilter{n}"]))
    
    # Selection tool
    selection = alt.selection_point(fields = [ss.primaryField])
    
    # Make the primary Chart
    title = f"Distribution of {ss.primaryField}"
    primary = alt.Chart(df.to_pandas(), title = title).mark_arc().encode(
        angle = "count()",
        color = f"{ss.primaryField}:N"
    ).add_params(selection)

    # Make the secondary plot (if we want one)
    if ss.secondaryField != "None":
        secondary = alt.Chart(df.to_pandas()).mark_bar().encode(
            x = ss.secondaryField,
            y = "count()",
            color = f"{ss.secondaryField}:N"
        )

    # Plot
    if ss.secondaryField == 'None':
        st.altair_chart(primary, theme = None)
    else:
        chart = primary | secondary
        chart.resolve_scale(color = 'independent')
        st.altair_chart(chart, theme = None)



if __name__ == '__main__':
    main()