import streamlit as st
import sqlite3
import hashlib
import re
from datetime import datetime
import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv
from space_track import SpaceTrackClient
import base64
from cryptography.fernet import Fernet
import json

# Load environment variables
load_dotenv()

# Generate a key for encryption (store this securely in production)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_credentials(username, password):
    """Encrypt credentials for secure storage."""
    credentials = {
        'username': username,
        'password': password,
        'timestamp': datetime.now().isoformat()
    }
    encrypted_data = cipher_suite.encrypt(json.dumps(credentials).encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_credentials(encrypted_data):
    """Decrypt stored credentials."""
    try:
        decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data))
        return json.loads(decrypted_data)
    except Exception as e:
        print(f"Error decrypting credentials: {e}")
        return None

def store_credentials(username, password):
    """Store encrypted credentials in session state."""
    encrypted = encrypt_credentials(username, password)
    st.session_state['stored_credentials'] = encrypted

def clear_stored_credentials():
    """Clear stored credentials from session state."""
    if 'stored_credentials' in st.session_state:
        del st.session_state['stored_credentials']

def load_stored_credentials():
    """Load and decrypt stored credentials if they exist."""
    if 'stored_credentials' in st.session_state:
        credentials = decrypt_credentials(st.session_state['stored_credentials'])
        if credentials:
            return credentials.get('username'), credentials.get('password')
    return None, None

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
    st.subheader("Space-Track.org Login (required for data access)")
    
    # Check for stored credentials
    stored_username, stored_password = load_stored_credentials()
    
    # Login form
    username = st.text_input("Space-Track Username", value=stored_username or "")
    password = st.text_input("Space-Track Password", type="password", value=stored_password or "")
    remember_me = st.checkbox("Remember Me", value=bool(stored_username))
    
    if st.button("Set Space-Track Credentials"):
        if username and password:
            try:
                client = SpaceTrackClient(username=username, password=password)
                if client.authenticate():
                    st.session_state['spacetrack_authenticated'] = True
                    st.session_state['spacetrack_username'] = username
                    st.session_state['spacetrack_password'] = password
                    # Store credentials if remember me is checked
                    if remember_me:
                        store_credentials(username, password)
                    else:
                        clear_stored_credentials()
                    st.success("Space-Track credentials set for this session.")
                    st.rerun()
                else:
                    # Clear session state and stored credentials on failed login
                    st.session_state['spacetrack_authenticated'] = False
                    st.session_state['spacetrack_username'] = ''
                    st.session_state['spacetrack_password'] = ''
                    clear_stored_credentials()
                    st.error("Failed to authenticate with Space-Track.org. Please check your credentials.")
                    st.rerun()
            except Exception as e:
                # Clear session state and stored credentials on error
                st.session_state['spacetrack_authenticated'] = False
                st.session_state['spacetrack_username'] = ''
                st.session_state['spacetrack_password'] = ''
                clear_stored_credentials()
                st.error(f"Authentication error: {e}")
                st.rerun()
        else:
            st.error("Please enter both username and password.")

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if not st.session_state['authenticated']:
        login_page()
        return False
    return True 