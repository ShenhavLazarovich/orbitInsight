import streamlit as st
<<<<<<< Updated upstream
import auth
import dashboard

# Set page configuration
st.set_page_config(
    page_title="OrbitInsight",
    page_icon="🛰️",
    layout="wide",
)

# Debug: Show session state for troubleshooting (remove after testing)
st.write("DEBUG session_state:", dict(st.session_state))

# Initialize authentication
auth.init_db()

# Show login page if not authenticated
if not st.session_state.get('spacetrack_authenticated'):
    auth.login_page()
else:
    dashboard.init_dashboard()

