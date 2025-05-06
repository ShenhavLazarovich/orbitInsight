import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px

import database as db
import analysis as an
import visualization as vis
import utils

# Set page configuration
st.set_page_config(
    page_title="Satellite Trajectory Analysis",
    page_icon="🛰️",
    layout="wide",
)

# Main title
st.title("Satellite Trajectory Analysis Dashboard")

# Check for Space-Track credentials
has_space_track_credentials = os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD")

# If credentials are missing, show a form to collect them
if not has_space_track_credentials:
    st.warning("Space-Track.org credentials are required to fetch real satellite data.")
    
    with st.form("space_track_credentials"):
        st.write("Please enter your Space-Track.org credentials:")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Save Credentials")
        
        if submitted and username and password:
            # Set environment variables
            os.environ["SPACETRACK_USERNAME"] = username
            os.environ["SPACETRACK_PASSWORD"] = password
            st.success("Credentials saved successfully! You can now access real satellite data.")
            has_space_track_credentials = True
            st.rerun()

# Sidebar for filters and controls
st.sidebar.header("Data Filters")

# Connect to database
try:
    engine = db.get_database_connection()
    # Get available satellites
    satellites = db.get_satellites(engine)
    
    if not satellites:
        st.warning("No satellite data found. Make sure Space-Track.org credentials are set.")
        st.stop()
        
except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")
    st.stop()

# Display source of the data
if has_space_track_credentials:
    st.sidebar.success("Using real-time data from Space-Track.org")
else:
    st.sidebar.info("Using locally cached satellite data")

# Satellite selection
selected_satellite = st.sidebar.selectbox(
    "Select Satellite ID",
    options=satellites,
    help="Choose a satellite to view its trajectory data"
)

# Time period selection
st.sidebar.subheader("Time Period")
today = datetime.now()
default_start_date = today - timedelta(days=7)

start_date = st.sidebar.date_input(
    "Start Date",
    value=default_start_date,
    help="Select start date for data filtering"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=today,
    help="Select end date for data filtering"
)

# Alert type filter
alert_types = db.get_alert_types(engine)
selected_alert_types = st.sidebar.multiselect(
    "Alert Types",
    options=alert_types,
    default=alert_types,
    help="Select alert types to include"
)

# Load data button
if st.sidebar.button("Load Data"):
    # Show loading spinner
    with st.spinner("Loading trajectory data..."):
        try:
            # Get data from database or Space-Track
            df = db.get_trajectory_data(
                engine, 
                selected_satellite, 
                start_date, 
                end_date, 
                selected_alert_types
            )
            
            if df.empty:
                if has_space_track_credentials:
                    st.warning(f"No data found for satellite {selected_satellite} in the selected date range. Try a different satellite or date range.")
                else:
                    st.warning("No data found. Please enter Space-Track.org credentials to access real satellite data.")
                st.stop()
                
            # Store the data in session state for reuse
            st.session_state['trajectory_data'] = df
            st.session_state['satellite_id'] = selected_satellite
            
            # Add satellite name to session state if available
            if 'satellite_name' in df.columns:
                satellite_name = df['satellite_name'].iloc[0]
                st.session_state['satellite_name'] = satellite_name
            
        except Exception as e:
            st.error(f"Error retrieving data: {str(e)}")
            st.stop()
    
    st.success(f"Loaded {len(df)} trajectory points for satellite {selected_satellite}")

# Display data and visualizations if data is loaded
if 'trajectory_data' in st.session_state:
    df = st.session_state['trajectory_data']
    satellite_id = st.session_state['satellite_id']
    
    # Display satellite name if available
    if 'satellite_name' in st.session_state:
        st.subheader(f"Satellite: {st.session_state['satellite_name']} (ID: {satellite_id})")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Data Table", "Visualizations", "Analysis"])
    
    with tab1:
        st.subheader("Trajectory Data")
        
        # Add simple data filtering options
        col1, col2 = st.columns(2)
        with col1:
            rows_to_display = st.number_input("Rows to display", min_value=10, max_value=1000, value=100, step=10)
        
        with col2:
            sort_by = st.selectbox("Sort by", options=df.columns)
            sort_order = st.radio("Sort order", options=["Ascending", "Descending"], horizontal=True)
        
        # Apply sorting
        if sort_order == "Ascending":
            df_display = df.sort_values(by=sort_by).head(rows_to_display)
        else:
            df_display = df.sort_values(by=sort_by, ascending=False).head(rows_to_display)
        
        # Display the data table
        st.dataframe(df_display, use_container_width=True)
        
        # Add download button
        csv = utils.convert_df_to_csv(df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"satellite_{satellite_id}_trajectory_{start_date}_{end_date}.csv",
            mime="text/csv",
        )
    
    with tab2:
        st.subheader("Trajectory Visualizations")
        
        # Select visualization type
        viz_type = st.radio(
            "Visualization Type",
            options=["2D Path", "3D Path", "Time Series", "Altitude Profile"],
            horizontal=True
        )
        
        # Display the selected visualization
        if viz_type == "2D Path":
            fig = vis.plot_2d_trajectory(df)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "3D Path":
            fig = vis.plot_3d_trajectory(df)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Time Series":
            # Select parameter for time series
            param = st.selectbox(
                "Select Parameter",
                options=[col for col in df.columns if col not in ['time', 'timestamp', 'date', 'satellite_id', 'alert_id', 'alert_type', 'satellite_name', 'object_name']],
                help="Select parameter to plot over time"
            )
            fig = vis.plot_time_series(df, param)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Altitude Profile":
            fig = vis.plot_altitude_profile(df)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Trajectory Analysis")
        
        # Basic statistics
        st.write("### Basic Statistics")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        stats_df = an.calculate_basic_stats(df[numeric_cols])
        st.dataframe(stats_df, use_container_width=True)
        
        # Trajectory Metrics
        st.write("### Trajectory Metrics")
        metrics = an.calculate_trajectory_metrics(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Distance (km)", f"{metrics['total_distance']:.2f}")
            st.metric("Average Speed (km/h)", f"{metrics['avg_speed']:.2f}")
        
        with col2:
            st.metric("Max Altitude (km)", f"{metrics['max_altitude']:.2f}")
            st.metric("Min Altitude (km)", f"{metrics['min_altitude']:.2f}")
        
        with col3:
            st.metric("Duration (hours)", f"{metrics['duration']:.2f}")
            st.metric("Alerts Count", metrics['alerts_count'])
        
        # Alert Analysis
        if 'alert_type' in df.columns and df['alert_type'].notna().any():
            st.write("### Alert Distribution")
            fig = an.plot_alert_distribution(df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Trajectory Anomaly Detection
        st.write("### Anomaly Detection")
        anomaly_param = st.selectbox(
            "Select Parameter for Anomaly Detection",
            options=[col for col in numeric_cols if col not in ['satellite_id', 'alert_id']],
            help="Select parameter to analyze for anomalies"
        )
        
        anomaly_threshold = st.slider(
            "Anomaly Threshold (standard deviations)",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1,
            help="Number of standard deviations from mean to consider as anomaly"
        )
        
        anomaly_df, anomaly_fig = an.detect_anomalies(df, anomaly_param, anomaly_threshold)
        st.plotly_chart(anomaly_fig, use_container_width=True)
        
        if not anomaly_df.empty:
            st.write(f"Found {len(anomaly_df)} anomalies in {anomaly_param}")
            st.dataframe(anomaly_df, use_container_width=True)
        else:
            st.info(f"No anomalies detected in {anomaly_param} with the current threshold.")

else:
    # Display instructions if no data is loaded
    st.info("👈 Select a satellite and time period, then click 'Load Data' to begin.")
    
    # Show sample information about the application
    st.write("""
    ## About This Application
    
    This dashboard allows you to access, visualize, and analyze real satellite trajectory data from the Space-Track.org database (Combined Space Operations Center).
    
    ### Features:
    - Connect to Space-Track.org API to fetch real satellite data
    - Store and cache data in a local database for faster access
    - Retrieve and filter data by satellite ID, time period, and alert type
    - View trajectory data in tabular format
    - Visualize satellite paths in 2D and 3D
    - Analyze trajectory parameters and detect anomalies
    - Export data to CSV format
    
    ### How It Works:
    1. If you have Space-Track.org credentials, the app will fetch real-time satellite data
    2. Data is calculated using the SGP4 orbital propagator from TLE (Two-Line Element) sets
    3. Results are cached in a local database for improved performance
    4. Visualizations and analysis are performed on the real orbital data
    
    To get started, use the sidebar to select a satellite and time period, then click the "Load Data" button.
    """)
