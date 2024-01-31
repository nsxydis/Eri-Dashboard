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

        dfGroup = dfGroup.with_columns(pl.col(dfGroup.columns[0]).map_elements(lambda x: ss[f'group{i}Name']).alias('group'))
        
        # Combine the groups or create the join dataframe
        if i == 1:
            dfJoin = dfGroup
        else:
            dfJoin = dfJoin.vstack(dfGroup)

    # Plot the scale data
    chart = alt.Chart(dfJoin.to_pandas()).mark_bar().encode(
        x = 'group',
        y = 'count()',
        color = 'value:N',
        column = 'variable:N',
        tooltip = [
            'group',
            'count()',
            'variable',
            'value'
        ]
    ).transform_filter(
        alt.datum.question == 'scale'
    )
    st.altair_chart(chart, theme = None)

    # Filter for the question of interest
    dfJoin = dfJoin.filter(pl.col('question') == ss['question'])
    dfJoin = dfJoin.filter(pl.col('question') != 'scale')

    if 'details' not in ss:
        noDetailsPlot(dfJoin)
    else:
        detailsPlot(dfJoin)

def noDetailsPlot(df):
    '''Plot if there are no details provided'''
    # Plot each of the filter groups together
    chart = alt.Chart(df.to_pandas()).mark_bar().encode(
        x = 'count()',
        y = 'group',
        color = 'value:N',
        row = 'variable',
        tooltip = [
            'count()',
            'variable',
            'group',
            'value'
        ]
    ).transform_filter(
        alt.datum.question == st.session_state['question']
    )
    st.altair_chart(chart, theme = None)

def detailsPlot(df):
    '''Question plots if we do have details'''
    cols = {}

    questions = sorted(df['variable'].unique().to_list(), key = str.casefold)
    details = st.session_state.details
    for question in questions:
        
        with st.container():
            col1, col2, col3 = st.columns(3)
            info = details.filter(pl.col('item name') == question)
            with col1:
                # Write out the question information
                st.write(f'## {question}')
                st.write(f"### Prompt: {info['question text'][0]}")

            # Plot the question
            chart = alt.Chart(df.to_pandas()).mark_bar().encode(
                x = 'count()',
                y = 'group',
                color = 'value:N',
                tooltip = [
                    'count()',
                    'variable',
                    'group',
                    'value'
                ]
            ).transform_filter(
                alt.datum.variable == question
            )
            with col2:
                st.altair_chart(chart, theme = None)
        
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