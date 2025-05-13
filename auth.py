import streamlit as st
import sqlite3
import hashlib
import re
from datetime import datetime
import streamlit_authenticator as stauth

# --- Local Auth Functions ---
def init_db():
    """Initialize the SQLite database for user authentication."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password_hash TEXT,
                  email TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?)',
                 (username, password_hash, email, datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('SELECT * FROM users WHERE username=? AND password_hash=?',
             (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user is not None

# --- Main Login Page ---
def login_page():
    st.title("Welcome to OrbitInsight")

    # --- Google OAuth ---
    authenticator = stauth.Authenticate(
        credentials={"usernames": {}},  # Fix: add empty usernames key
        cookie_name="orbitinsight",
        key="auth",
        cookie_expiry_days=1,
        oauth={
            "provider": "google",
            "client_id": "YOUR_GOOGLE_CLIENT_ID",
            "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
            "redirect_uri": "http://localhost:8501"
        }
    )
    name, authentication_status, username = authenticator.login("Login with Google", "main")
    if authentication_status:
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.success(f"Logged in as {username} (Google)")
        st.rerun()
    elif authentication_status is False:
        st.error("Google login failed")

    st.markdown("---")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab2:
        st.subheader("Create Account")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        email = st.text_input("Email", key="signup_email")
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Invalid email address")
            elif register_user(new_username, new_password, email):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists")

    with st.expander("Forgot Password?"):
        reset_username = st.text_input("Username", key="reset_username")
        new_password = st.text_input("New Password", type="password", key="reset_new_password")
        if st.button("Reset Password"):
            if reset_username and new_password:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                password_hash = hash_password(new_password)
                c.execute('UPDATE users SET password_hash=? WHERE username=?', (password_hash, reset_username))
                if c.rowcount > 0:
                    st.success("Password reset successful! Please login.")
                else:
                    st.error("Username not found.")
                conn.commit()
                conn.close()
            else:
                st.error("Please enter both username and new password.")

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if not st.session_state['authenticated']:
        login_page()
        return False
    return True 