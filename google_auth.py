import streamlit as st
from streamlit_oauth import OAuth2Component
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def google_login():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://localhost:8501"
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    scope = "openid email profile"

    oauth2 = OAuth2Component(
        client_id=client_id,
        client_secret=client_secret,
        authorize_endpoint=authorization_url,
        token_endpoint=token_url,
        redirect_uri=redirect_uri,
        scope=scope,
        key="google"
    )

    token = oauth2.authorize_button("Sign in with Google")
    if token and "id_token" in token:
        import jwt
        user_info = jwt.decode(token["id_token"], options={"verify_signature": False})
        st.session_state['authenticated'] = True
        st.session_state['username'] = user_info.get("email")
        st.session_state['google_user'] = user_info
        st.success(f"Signed in as {user_info.get('email')}")
        st.rerun()
    return token 