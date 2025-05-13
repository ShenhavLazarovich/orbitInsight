import streamlit as st
import auth

# Set page configuration
st.set_page_config(
    page_title="OrbitInsight",
    page_icon="🛰️",
    layout="wide",
)

# Initialize authentication
auth.init_db()

# Show login page if not authenticated
if not st.session_state.get('authenticated'):
    auth.login_page()
else:
    st.title("OrbitInsight Dashboard")
    st.write(f"Welcome, {st.session_state['username']}!")
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.rerun()

