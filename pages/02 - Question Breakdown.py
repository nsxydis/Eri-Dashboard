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

    # Melt the dataframe
    df = ss.df.melt(id_vars = baseVars)

    # Find the associated questions
    df = df.with_columns(pl.col('variable').map_elements(lambda x: associatedQuestion(x)).alias('question'))

    # Filter out null and missing data from the melt
    # NOTE: This assumes all your data is numeric!
    df = df.filter(
        (pl.col('value').is_not_null()) &
        (pl.col('value').str.strip_chars() != "")
    )
    df = df.cast({'value' : int})
    df = df.filter(pl.col('value') >= 0)

    # Page options
    with st.sidebar:
        # Get all the possible questions
        questions = df[['question']].unique()
        
        # Remove base variables and scale items
        questions = questions.filter(pl.col('question').str.ends_with('baseVar') == False)
        questions = questions.filter(pl.col('question').str.ends_with('scale') == False)
        questions = questions['question'].unique().to_list()
        questions = sorted(questions, key = str.casefold)

        # Ask the user which question they'd like to view
        ph.ss('question', questions[0])
        index = questions.index(ss['question'])
        st.selectbox('Display Question', options = questions, key = 'question', index = index)

    # Group results + Add group name
    ph.ss('numGroups', 1)
    for i in range(1, ss.numGroups + 1):
        dfGroup = ph.filterDataframe(i, df = df)
        
        # Init if needed
        ph.ss(f'group{i}Name', f'Group {i}')

        # If we got an error, skip filtering
        if type(dfGroup) == type(123) and dfGroup > 0:
            dfGroup = df

        if len(dfGroup) > 0:
            dfGroup = dfGroup.with_columns(pl.col(dfGroup.columns[0]).map_elements(lambda x: ss[f'group{i}Name']).alias('group'))
        else:
            st.error(f"No data found for {ss[f'group{i}Name']}")
            continue

        # Check for null data
        if len(dfGroup['group'].is_null()) > 0:
            st.warning(f"Null data detected in {ss[f'group{i}Name']} and filtered from the results")
            dfGroup = dfGroup.filter(pl.col('group').is_not_null())

        # Aggregate the data        
        dfGroup = dfGroup.group_by(
            ['group', 'variable', 'question']
        ).agg([
            (pl.col('value').sum() / pl.col('value').count()).alias('value'),
            (pl.col('value').count()).alias('total')
        ])

        # Combine the groups or create the join dataframe
        if i == 1:
            dfJoin = dfGroup
        else:
            dfJoin = dfJoin.vstack(dfGroup)

    # Clean up memory
    del df, dfGroup

    # Make the scale chart
    title = "Nice chart"
    chart = alt.Chart(dfJoin.to_pandas(), title = title).mark_bar().encode(
        x = 'group',
        y = alt.Y('value', scale = alt.Scale(domain = [0, 1])),
        color = 'group',
        column = 'variable',
        tooltip = [
            alt.Tooltip('variable', title = 'Question'),
            'group',
            alt.Tooltip('value', title = 'Percent', format = '.2%'),
            alt.Tooltip('total', title = "Responses")
        ]
    ).transform_filter(
        alt.datum.question == 'scale',
    ).transform_filter(
        alt.datum.total >= 10
    )
    st.altair_chart(chart, theme = None)

    if 'details' not in ss:
        noDetailsPlot(dfJoin)
    else:
        detailsPlot(dfJoin)

def noDetailsPlot(df):
    '''Plot if there are no details provided'''
    # Plot each of the filter groups together
    chart = alt.Chart(df.to_pandas()).mark_bar().encode(
        x = alt.X('value', scale = alt.Scale(domain = [0, 1])),
        y = 'group',
        color = 'group',
        row = 'variable',
        tooltip = [
            alt.Tooltip('variable', title = 'Question'),
            'group',
            alt.Tooltip('value', title = 'Percent', format = '.2%'),
            alt.Tooltip('total', title = "Responses")
        ]
    ).transform_filter(
        alt.datum.question == st.session_state['question']
    ).transform_filter(
        alt.datum.total >= 10
    )
    st.altair_chart(chart, theme = None)

def detailsPlot(df):
    '''Question plots if we do have details'''
    cols = {}

    # Filter for the question we're looking at
    df = df.filter(pl.col('question') == st.session_state['question'])

    questions = sorted(df['variable'].unique().to_list(), key = str.casefold)
    details = st.session_state.details
    
    # Make the main chart we want to display
    chart = alt.Chart(df.to_pandas()).mark_bar().encode(
        x = alt.X('value', scale = alt.Scale(domain = [0, 1])),
        y = 'group',
        color = 'group',
        row = 'variable',
        tooltip = [
            alt.Tooltip('variable', title = 'Question'),
            'group',
            alt.Tooltip('value', title = 'Percent', format = '.2%'),
            alt.Tooltip('total', title = "Responses")
        ]
    ).transform_filter(
        # Only show results that have more than 10 responses
        alt.datum.total >= 10
    )

    for question in questions:
        
        with st.container():
            col1, col2, col3 = st.columns(3)
            info = details.filter(pl.col('item name') == question)
            with col1:
                # Write out the question information
                st.write(f'## {question}')

                # If we didn't get any data, we're missing the prompt
                if len(info) > 0:
                    st.write(f"### Prompt:")
                    st.write(f"{info['question text'][0]}")

            # Plot the question
            display = chart.transform_filter(
                alt.datum.variable == question
            )
            with col2:
                st.altair_chart(display, theme = None)
        
            st.markdown('---')

def associatedQuestion(variable):
    '''Returns the question for a given column name variable
    NOTE: If the variable is not a question, returns baseVar
    NOTE: If the variable is a scale value, returns scale'''

    a = variable.split('_')
    if a[-1] == 'scale':
        return 'scale'
    elif a[-1].isalpha():
        return 'baseVar'
    else:
        return variable.strip(f'_{a[-1]}')
 
if __name__ == "__main__":
    main()

    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass