'''
Purpose: Displays results for the individual questions.
'''

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

    # Identify our base variables
    baseVars = [var for var in ss.df.columns if associatedQuestion(var) == 'baseVar']

    # Page options
    with st.sidebar:
        st.slider("Groups to plot", 1, 5, key = 'numGroups')

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
            ph.filter(i)

    # Filter the dataframe
    df = ph.filterDataframe()
    
    # Melt the dataframe
    df = df.melt(id_vars = baseVars)

    # Find the associated questions
    df = df.with_columns(pl.col('variable').map_elements(lambda x: associatedQuestion(x)).alias('question'))

    # Figure out which items are scale variables
    df = df.with_columns(pl.col('variable').str.ends_with('scale').alias('scale'))

    # Selection tool
    selection = alt.selection_point(fields = ['question'])
    
    # Plot the scale
    scaleChart = alt.Chart(df.to_pandas()).mark_bar().encode(
        x = 'variable',
        y = 'count()',
        color = 'value',
        tooltip = [
            'variable',
            'count()',
            'question'
        ]
    ).add_params(selection
    ).transform_filter(
        alt.datum.scale == True
    )

    # Make the questions chart
    questionChart = alt.Chart(df.to_pandas()).mark_bar().encode(
        x = 'count()',
        color = 'value',
        row = 'variable',
        tooltip = [
            'variable',
            'question',
            'count()',
            'value'
        ]
    ).transform_filter(
        selection,
    ).transform_filter(
        alt.datum.scale == False
    )

    st.altair_chart(alt.vconcat(scaleChart, questionChart).resolve_scale(color = 'independent'), theme = None)
    st.dataframe(df)

def associatedQuestion(variable):
    '''Returns the question for a given column name variable
    NOTE: If the variable is not a question, returns baseVar'''

    a = variable.split('_')
    string = a[0]
    baseVar = True
    for item in a[1:]:
        if item == 'scale':
            baseVar = False
            break
        
        if item.isalpha() == False:
            break
        else:
            baseVar = False
            string += f"_{item}"

    # If there isn't a number or 'scale' found, it's a base var
    if baseVar:
        return "baseVar"
    else:
        return string
    
if __name__ == "__main__":
    main()

    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass