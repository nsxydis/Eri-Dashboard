'''
Purpose: Code to filter the data by.
'''

import streamlit as st
import polars as pl
import pageHelper as ph

def main():
    st.slider("Groups to plot", 1, 5, key = 'numGroups')

    for i in range(1, ss.numGroups + 1):
        # Headings
        st.markdown("###")
        st.write(f"# Group {i}")
        st.markdown("###")
        
        # Dataframe filtering
        filter(i)

def filter(i):
    '''Code to write the data filter options on the sidebar''' 
    st.write('# Filtering Data')
    fieldKey = f'fields{i}'
    ph.ss(fieldKey, [])
    st.multiselect("Filter Fields", options = st.session_state.df.columns, key = fieldKey, default=st.session_state[fieldKey])

    # For each field, give options to filter by
    for n in range(len(st.session_state[fieldKey])):
        item = st.session_state[fieldKey][n]
        key = f'field{i}Filter{n}'
        ph.ss(key, [])
        st.multiselect(f"Filter {item}", options = st.session_state.df[item].unique().to_list(), key = key, default = st.session_state[key])

if __name__ == '__main__':
    main()
    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass