import streamlit as st
import sqlite3
from datetime import datetime

def init_feedback_db():
    """Initialize the SQLite database for feedback."""
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  feedback_type TEXT,
                  message TEXT,
                  created_at TIMESTAMP,
                  status TEXT DEFAULT 'pending')''')
    conn.commit()
    conn.close()

def submit_feedback(username, feedback_type, message):
    """Submit user feedback."""
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (username, feedback_type, message, created_at) VALUES (?, ?, ?, ?)',
             (username, feedback_type, message, datetime.now()))
    conn.commit()
    conn.close()

def show_feedback_form():
    """Display the feedback form."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Feedback & Support")
    
    feedback_type = st.sidebar.selectbox(
        "Type of Feedback",
        ["Bug Report", "Feature Request", "General Feedback", "Support Request"]
    )
    
    message = st.sidebar.text_area("Your Message", height=100)
    
    if st.sidebar.button("Submit Feedback"):
        if message.strip():
            submit_feedback(
                st.session_state.get('username', 'anonymous'),
                feedback_type,
                message
            )
            st.sidebar.success("Thank you for your feedback!")
        else:
            st.sidebar.error("Please enter a message")

def show_support_resources():
    """Display support resources."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Support Resources")
    
    st.sidebar.markdown("""
    - [User Guide](https://github.com/yourusername/orbitinsight/blob/main/USER_GUIDE.md)
    - [FAQ](https://github.com/yourusername/orbitinsight/wiki/FAQ)
    - [Report Issues](https://github.com/yourusername/orbitinsight/issues)
    - [Contact Support](mailto:support@orbitinsight.com)
    """)

def init_feedback():
    """Initialize feedback system."""
    if 'feedback' not in st.session_state:
        st.session_state['feedback'] = []
    init_feedback_db()
    show_feedback_form()
    show_support_resources() 