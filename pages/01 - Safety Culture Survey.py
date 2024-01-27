import streamlit as st
import polars as pl
import altair as alt
import pageHelper as ph

# Suppress Error reporting
from streamlit.elements.utils import _shown_default_value_warning
_shown_default_value_warning = False

def main():
    # Page initialization, stop on error
    if ph.init() != 0:
        return

    # Shorthand
    ss = st.session_state

    # Debugging...
    # st.write(ss)

    # TODO: Fix where the fullscreen button appears
    style_fullscreen_button_css = """
    button[title="View fullscreen"] {
        right: 0;
        position: relative;
    }
    """
    st.markdown(
        "<style>"
        + style_fullscreen_button_css
        + "</styles>",
        unsafe_allow_html=True,
    )

    # Page options
    with st.sidebar:
        # Heading
        st.write('# Plotting Data')
        # Field to separate by
        key = 'primaryField'
        ph.ss(key, "None")
        primaryColumns = ["None"] + ss.df.columns.copy()
        st.selectbox("Primary Breakdown Field", options = primaryColumns, key = key, index = primaryColumns.index(ss[key]))
            
        # Secondary Plots
        if ss.primaryField:
            secondaryColumns = ss.df.columns.copy()
            if ss.primaryField != "None":
                secondaryColumns.remove(ss.primaryField)
            secondaryColumns = ['None'] + secondaryColumns
            key = 'secondaryField'
            ph.ss(key, "None")
            st.selectbox("Secondary Breakdown Field", options = secondaryColumns, key = 'secondaryField', index = secondaryColumns.index(ss[key]))

        # Filters
        st.markdown("---") # Horizontal Line
        st.write('# Filtering Data')
        key = 'fields'
        ph.ss(key, [])
        st.multiselect("Filter Fields", options = ss.df.columns, key = key, default=ss[key])

        # For each field, give options to filter by
        for n in range(len(ss["fields"])):
            item = ss[f'fields'][n]
            key = f'fieldFilter{n}'
            ph.ss(key, [])
            st.multiselect(f"Filter {item}", options = ss.df[item].unique().to_list(), key = key, default = ss[key])

    # Stop if we don't have a primary field
    if not ss.primaryField or ss.primaryField == "None":
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

    # Chart header
    if ss.secondaryField and ss.secondaryField != "None":
        st.write("# Click on the pie chart to change the secondary chart")
        st.write(f"You can select multiple {ss.primaryField} values by holding shift when you click")
        st.write("Click just outside the pie chart to remove your selection")
        st.write("At the top left of the chart area is a button to expand the chart to fullscreen mode (recommended)")
    
    # Selection tool
    selection = alt.selection_point(fields = [ss.primaryField], encodings = ['color'])
    
    # Allows tooltips to work when in fullscreen mode
    st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
        unsafe_allow_html=True)

    # Make the primary Chart
    title = f"Distribution of {ss.primaryField}"
    primary = alt.Chart(df.to_pandas(), title = title).mark_arc().encode(
        angle = "count()",
        color = alt.condition(selection, f"{ss.primaryField}:N", alt.value('lightgray'))
    ).add_params(selection)

    # Make the secondary plot (if we want one)
    if ss.secondaryField and ss.secondaryField != "None":
        # TODO: Get the text of the selected fields
        text = alt.Chart(df.to_pandas()).mark_text(dy=-200, size=20).encode(
            text = f'{ss.primaryField}:O',
            color = alt.value('white')
        ).transform_filter(selection)

        # Secondary chart
        title = [f"Overall Distribution", f"of {ss.secondaryField}"]
        secondary = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss.secondaryField}:N",
            y = 'count()',
            color = f"{ss.secondaryField}:N",
            tooltip = [
                ss.secondaryField,
                'count()'
            ]
        ).transform_filter(selection)

        full = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss.secondaryField}:N",
            y = 'count()',
            color = f"{ss.secondaryField}:N",
            opacity = alt.value(0.3)
        )
        
        # Secondary Chart with percentages
        title = ["Distribution of selection", f"for {ss.secondaryField}"]
        pctSecondary = alt.Chart(df.to_pandas(), title = title).mark_bar().encode(
            x = f"{ss.secondaryField}:N",
            y = alt.Y("sum(pct):Q", axis = alt.Axis(format = '%')),
            color = f"{ss.secondaryField}:N",
            tooltip = [
                ss.secondaryField,
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
    if not ss.secondaryField or ss.secondaryField == 'None':
        st.altair_chart(primary, theme = None)
    else:
        chart = primary | (secondary + full) | pctSecondary
        st.altair_chart(chart.resolve_scale(color = 'independent'), theme = None)

if __name__ == '__main__':
    main()

    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        st.session_state[k] = v