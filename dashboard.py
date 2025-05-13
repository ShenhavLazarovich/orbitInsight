import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

import database as db
import analysis as an
import visualization as vis
import utils
import auth
import feedback

def show_dashboard():
    """Display the main dashboard."""
    st.header("Welcome to OrbitInsight")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Satellites", "2,500+")
    with col2:
        st.metric("Launch Sites", "25")
    with col3:
        st.metric("Recent Alerts", "15")
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("Dashboard under construction. More features coming soon!")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Satellite Trajectory"):
            st.session_state['page'] = "Satellite Trajectory"
            st.rerun()
    with col2:
        if st.button("Check Recent Alerts"):
            st.session_state['page'] = "Conjunction Data"
            st.rerun()

def show_satellite_trajectory():
    """Display satellite trajectory analysis."""
    st.header("Satellite Trajectory Analysis")
    st.info("Satellite trajectory analysis feature coming soon!")

def show_catalog_data():
    """Display satellite catalog data."""
    st.header("Satellite Catalog")
    st.info("Satellite catalog feature coming soon!")

def show_launch_sites():
    """Display launch sites data."""
    st.header("Launch Sites")
    st.info("Launch sites feature coming soon!")

def show_decay_data():
    """Display decay data."""
    st.header("Decay Events")
    st.info("Decay events feature coming soon!")

def show_conjunction_data():
    """Display conjunction data."""
    st.header("Conjunction Events")
    st.info("Conjunction events feature coming soon!")

def show_boxscore_data():
    """Display boxscore data."""
    st.header("Boxscore Statistics")
    st.info("Boxscore statistics feature coming soon!")

def init_dashboard():
    """Initialize the dashboard layout."""
    # Check authentication
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access the dashboard.")
        return
    
    # Main dashboard layout
    st.title("OrbitInsight Dashboard")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Satellite Trajectory", "Catalog Data", "Launch Sites", "Decay Data", "Conjunction Data", "Boxscore Data"]
    )
    
    # User info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Logged in as: **{st.session_state['username']}**")
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.rerun()
    
    # Main content area
    if page == "Dashboard":
        show_dashboard()
    elif page == "Satellite Trajectory":
        show_satellite_trajectory()
    elif page == "Catalog Data":
        show_catalog_data()
    elif page == "Launch Sites":
        show_launch_sites()
    elif page == "Decay Data":
        show_decay_data()
    elif page == "Conjunction Data":
        show_conjunction_data()
    elif page == "Boxscore Data":
        show_boxscore_data() 