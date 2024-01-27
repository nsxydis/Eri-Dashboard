import streamlit as st

st.write(st.session_state)

for k, v in st.session_state.items():
    st.session_state[k] = v