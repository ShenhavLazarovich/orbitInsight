import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px

import space_track as st_api
import analysis as an
import visualization as vis
import utils

# Set page configuration
st.set_page_config(
    page_title="OrbitInsight",
    page_icon="🛰️",
    layout="wide",
)

# Add our custom CSS files
def add_custom_css():
    # Include our external CSS file
    with open('static/custom.css', 'r', encoding='utf-8') as css_file:
        css_content = css_file.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Initialize Space-Track client
@st.cache_resource
def get_space_track_client():
    return st_api.SpaceTrackClient()

# Get satellite data from Space-Track
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_satellites(search_query=None):
    client = get_space_track_client()
    satellites_dict = {}
    
    # Add default well-known satellites
    default_satellites = {
        "25544": "ISS (International Space Station)",
        "20580": "Hubble Space Telescope",
        "41866": "GOES-16 (Weather Satellite)",
        "39084": "Landsat-8 (Earth Observation)",
        "25994": "Terra (Earth Observation)",
        "99001": "OpSat3000 (Earth Observation)"
    }
    satellites_dict.update(default_satellites)
    
    # If search query provided, search Space-Track
    if search_query:
        try:
            results = client.get_latest_tle(satellite_name=search_query, limit=10)
            for _, sat in results.iterrows():
                sat_id = sat['NORAD_CAT_ID']
                sat_name = sat['OBJECT_NAME']
                satellites_dict[sat_id] = sat_name
        except Exception as e:
            st.error(f"Error searching satellites: {e}")
    
    return satellites_dict

# Get trajectory data from Space-Track
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_trajectory_data(satellite_id, start_date, end_date):
    client = get_space_track_client()
    
    try:
        # Get latest TLE data
        tle_data = client.get_latest_tle(norad_cat_id=satellite_id, limit=1)
        if tle_data.empty:
            st.error(f"No TLE data found for satellite {satellite_id}")
            return pd.DataFrame()
            
        # Calculate positions
        positions = client.get_satellite_positions(
            tle_data,
            start_date,
            end_date,
            time_step_minutes=5
        )
        
        return positions
    except Exception as e:
        st.error(f"Error getting trajectory data: {e}")
        return pd.DataFrame()

# Main app layout
def main():
    st.title("OrbitInsight 🛰️")
    add_custom_css()
    
    # Sidebar for satellite selection
    st.sidebar.title("Satellite Selection")
    
    # Search box for satellites
    search_query = st.sidebar.text_input("Search satellites", "")
    
    # Get available satellites
    satellites = get_satellites(search_query)
    
    # Dropdown for satellite selection
    selected_satellite = st.sidebar.selectbox(
        "Select a satellite",
        options=list(satellites.keys()),
        format_func=lambda x: satellites[x]
    )
    
    # Date range selection
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End date", datetime.now())
    
    # Get trajectory data
    trajectory_data = get_trajectory_data(selected_satellite, start_date, end_date)
    
    if not trajectory_data.empty:
        # Display trajectory visualization
        st.subheader("Satellite Trajectory")
        fig = vis.plot_trajectory(trajectory_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Orbit Statistics")
        stats = an.calculate_orbit_statistics(trajectory_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Altitude", f"{stats['avg_altitude']:.2f} km")
        with col2:
            st.metric("Orbit Period", f"{stats['orbit_period']:.2f} min")
        with col3:
            st.metric("Max Velocity", f"{stats['max_velocity']:.2f} km/s")
    else:
        st.warning("No trajectory data available for the selected satellite and time range.")

if __name__ == "__main__":
    main() 