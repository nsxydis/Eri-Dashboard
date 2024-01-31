'''
Purpose: Code to filter the data by.
'''

import streamlit as st
import polars as pl
import pageHelper as ph

def main():
    # Page initialization, stop on error
    if ph.init() != 0:
        return
    
    # Shorthand
    ss = st.session_state
    
    # Number of groups we want to filter and plot
    ph.ss('numGroups', 1)
    st.slider("Groups to plot", 1, 5, key = 'numGroups', value = ss['numGroups'])

    # Fields we want to filter for each group
    fieldKey = 'fields'
    ph.ss(fieldKey, [])
    st.multiselect("Filter Fields", options = ss.df.columns, key = fieldKey, default = ss[fieldKey])
    
    # Stop if we don't have anything to filter
    if len(st.session_state[fieldKey]) == 0:
        st.markdown("---")
        st.write("Select fields to filter by!")
        return 1
    
    # Filter form
    with st.form("filterGroups"):
        st.form_submit_button("Apply Groupings!")
        st.markdown("---")
        for i in range(1, ss.numGroups + 1):
            # Headings
            ph.ss(f'group{i}Name', f"Group {i}")
            st.write("# " + ss[f"group{i}Name"])

            # Get the Group name
            st.text_input(f'Group {i} Name', key = f'group{i}Name', value = ss[f'group{i}Name'])

            # Make a groupDict, if needed
            ph.ss(f'groupDict{i}', {})
            
            # Dataframe filtering
            filter(i)
            st.markdown("---")
        st.form_submit_button("Apply Groupings! ")

def filter(i):
    '''Code to write the data filter options on the sidebar'''
    ss = st.session_state
    dictionary = ss[f"groupDict{i}"]
    
    # Add the keys to our dictionary
    for field in ss.fields:
        if field not in dictionary:
            dictionary[field] = []

    # Filter options
    for key in ss.fields:
        values = st.multiselect(f"Filter {key}", options = ss.df[key].unique().to_list(), key = f'jambox{key}{i}', default = dictionary[key])
        dictionary[key] = values

if __name__ == '__main__':
    main()
    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass