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

    # Page options
    with st.sidebar:
        for i in range(1, ss.numGroups + 1):
            # Headings
            st.markdown("###")
            st.write(f"# Group {i}")
            st.markdown("###")
            st.write('# Plotting Data')
            # Field to separate by
            key = f'primaryField{i}'
            ph.ss(key, "None")
            primaryColumns = ["None"] + ss.df.columns.copy()
            st.selectbox("Primary Breakdown Field", options = primaryColumns, key = key, index = primaryColumns.index(ss[key]))
                
            # Secondary Plots
            if ss[key]:
                secondaryColumns = ss.df.columns.copy()
                if ss[key] != "None":
                    secondaryColumns.remove(ss[key])
                secondaryColumns = ['None'] + secondaryColumns
                key = f'secondaryField{i}'
                ph.ss(key, "None")
                st.selectbox("Secondary Breakdown Field", options = secondaryColumns, key = key, index = secondaryColumns.index(ss[key]))

            # Filters
            st.markdown("---") # Horizontal Line
            # ph.filter(i)

    # Main Page
    # Chart header
    st.write("# Click on the pie chart to change the secondary chart")
    st.write(f"You can select multiple values by holding shift when you click")
    st.write("Click just outside the pie chart to remove your selection")
    st.write("At the top left of the chart area is a button to expand the chart to fullscreen mode (recommended)")

    # Plotting loop
    for i in range(1, ss.numGroups + 1):
        mainChart(i)

def mainChart(i):
    '''Creates the main chart'''
    # Shorthand
    ss = st.session_state

    # Horizontal line
    st.markdown("---")

    # Header
    st.write(f"# Group {i}")

    # Display data filters
    fields = ss[f"fields"]
    if len(fields) > 0:
        st.write("## Filters")
        for field in fields:
            st.write(f"### Field: {field}")
            filters = ss[f"groupDict{i}"][field]
            if len(filters) > 0:
                st.write(filters)
            else:
                st.write("No items filtered for this field")

    # Horizontal line
    st.markdown("---")

    # Stop if we don't have a primary field
    primaryKey = f'primaryField{i}'
    if not ss[primaryKey] or ss[primaryKey] == "None":
        st.write(f"Select a Primary Breakdown Field for Group {i} first")
        return 1
    
    # Filter the dataframe
    df = ph.filterDataframe(i)

    # If there is not enough data in a filter, stop executing
    if len(df) < 10:
        string = f"There is not enough data for Group {i} ({len(df)} results; Need at least 10). "
        string += "Please select more data to see the results."
        st.error(string)
        return 2
    
    # Selection tool
    selection = alt.selection_point(fields = [ss[primaryKey]], encodings = ['color'])

    # Make the primary Chart
    title = f"Distribution of {ss[primaryKey]}"
    primary = alt.Chart(df.to_pandas(), title = title).mark_arc().encode(
        angle = "count()",
        color = alt.condition(selection, f"{ss[primaryKey]}:N", alt.value('lightgray'))
    ).add_params(selection)

    # Make the secondary plot (if we want one)
    secondaryKey = f"secondaryField{i}"
    if ss[secondaryKey] and ss[secondaryKey] != "None":
        # TODO: Get the text of the selected fields
        text = alt.Chart(df.to_pandas()).mark_text(dy=-200, size=20).encode(
            text = f'{ss[primaryKey]}:O',
            color = alt.value('white')
        ).transform_filter(selection)

        # Secondary chart
        title = [f"Overall Distribution", f"of {ss[secondaryKey]}"]
        secondary = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss[secondaryKey]}:N",
            y = 'count()',
            color = f"{ss[secondaryKey]}:N",
            tooltip = [
                ss[secondaryKey],
                'count()'
            ]
        ).transform_filter(selection)

        full = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss[secondaryKey]}:N",
            y = 'count()',
            color = f"{ss[secondaryKey]}:N",
            opacity = alt.value(0.3)
        )
        
        # Secondary Chart with percentages
        title = ["Distribution of selection", f"for {ss[secondaryKey]}"]
        pctSecondary = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss[secondaryKey]}:N",
            y = alt.Y("sum(pct):Q", axis = alt.Axis(format = '%')),
            color = f"{ss[secondaryKey]}:N",
            tooltip = [
                ss[secondaryKey],
                'count()',
                alt.Tooltip('sum(pct):Q', format = '%')
            ]
        ).transform_filter(selection
        ).transform_joinaggregate(
            total='count(*)'
        ).transform_calculate(
            pct='1 / datum.total'
        )

    # Plot
    if not ss[secondaryKey] or ss[secondaryKey] == 'None':
        st.altair_chart(primary, theme = None)
    else:
        chart = primary | (secondary + full) | pctSecondary
        st.altair_chart(chart.resolve_scale(color = 'independent'), theme = None)

if __name__ == '__main__':
    main()
    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass