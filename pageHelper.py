import streamlit as st
import polars as pl

# Suppress Error reporting
from streamlit.elements.utils import _shown_default_value_warning
_shown_default_value_warning = True

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

def filterDataframe(i, df = None):
    '''Filters the dataframe based on the current session_state'''
    if type(df) == type(None):
        # Make a copy of the data
        df = st.session_state.df.clone()

    # Filter Criteria
    dictionary = st.session_state[f"groupDict{i}"]
    fields = st.session_state[f"fields"]

    # Start subsetting
    for field in fields:
        # If nothing was selected to filter, skip
        if len(dictionary[field]) == 0:
            continue
        # Otherwise apply the filter
        else:
            df = df.filter(pl.col(field).is_in(dictionary[field]))
    return df