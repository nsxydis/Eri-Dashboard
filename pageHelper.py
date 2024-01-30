import streamlit as st
import polars as pl

def init():
    '''Default start for all pages'''
    # If we haven't used the dashboard page yet...
    if 'df' not in st.session_state:
        st.write("Go back to the dashboard page!")
        st.write("You need to upload a csv file.")
        return 1
    
    # Allows tooltips to work when in fullscreen mode
    st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
        unsafe_allow_html=True)
    
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
    
    # If there are no failures...
    return 0

def ss(variable, value = None):
    '''Checks if a variable is in the session state and sets its value if not'''
    if variable not in st.session_state:
        st.session_state[variable] = value

def filterDataframe(i):
    '''Filters the dataframe based on the current session_state'''
    # Make a copy of the data
    df = st.session_state.df.clone()

    # Start subsetting...
    for n in range(len(st.session_state[f'fields{i}'])):
        # Skip if nothing was selected for a field
        if len(st.session_state[f"field{i}Filter{n}"]) == 0:
            continue

        # Otherwise get the field and filter the data
        field = st.session_state[f"fields{i}"][n]
        df = df.filter(pl.col(field).is_in(st.session_state[f"field{i}Filter{n}"]))

    return df