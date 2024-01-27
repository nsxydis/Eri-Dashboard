import streamlit as st

st.write(st.session_state)

# Each page needs this for the session state to persist
for k, v in st.session_state.items():
    st.session_state[k] = v