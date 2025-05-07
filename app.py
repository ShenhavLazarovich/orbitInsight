import streamlit as st
import pandas as pd
import numpy as np
import os
import random
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

# Apply custom styling to replace the Replit runner icon with satellite icon
def replace_replit_running_icon():
    st.markdown("""
    <style>
    /* Target the Replit runner icon in the header */
    .runner-header-icon svg,
    .run-status-indicator {
        display: none !important;
    }
    
    /* Add our own satellite icon */
    .runner-header-icon::before,
    .run-status-indicator::before {
        content: "🛰️";
        font-size: 1.2rem;
        margin-right: 0.5rem;
        animation: satellite-spin 4s linear infinite;
        display: inline-block;
    }
    
    @keyframes satellite-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Style running text */
    .run-status-running::after {
        content: "SATELLITE ACTIVE...";
        font-weight: bold;
        color: #4CAF50;
    }
    
    /* Hide the original RUNNING... text */
    .run-status-running > span {
        display: none !important;
    }
    
    /* Also inject our styling for the loading spinner */
    .stSpinner > div {
        border-top-color: #1e88e5 !important;
        border-right-color: transparent !important;
        border-bottom-color: transparent !important;
        border-left-color: transparent !important;
    }
    
    /* Change the webview loading icon */
    @keyframes orbit {
        0% { transform: rotate(0deg) translateX(12px) rotate(0deg); }
        100% { transform: rotate(360deg) translateX(12px) rotate(-360deg); }
    }
    
    .loading-icon::before {
        content: "🛰️";
        font-size: 24px;
        animation: orbit 2s linear infinite;
        position: absolute;
        display: block;
    }
    
    .loading-icon > * {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the custom styling
replace_replit_running_icon()

# Add a custom satellite-themed loading animation using pure CSS
def add_satellite_css():
    st.markdown("""
    <style>
    .satellite-container {
        text-align: center;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
        background-color: rgba(0, 0, 0, 0.1);
        position: relative;
        height: 150px;
    }
    
    /* Table filter styles */
    .filter-container {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    .filter-title {
        font-weight: bold;
        color: #3e64ff;
        margin-bottom: 5px;
    }
    
    .filter-active {
        border-left: 3px solid #3e64ff;
        padding-left: 8px;
    }
    
    /* Space background styles */
    .space-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #0c1445;
        overflow: hidden;
        border-radius: 5px;
        z-index: 0;
    }
    
    /* Stars styles */
    .star {
        position: absolute;
        background-color: white;
        border-radius: 50%;
        animation: twinkle 2s infinite alternate;
    }
    
    @keyframes twinkle {
        0% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    /* Planet styles */
    .planet {
        position: absolute;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #1e5799, #207cca);
        box-shadow: 0 0 20px 2px rgba(32, 124, 202, 0.3);
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 1;
    }
    
    /* Planet rings */
    .planet-rings {
        position: absolute;
        width: 70px;
        height: 20px;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%) rotate(15deg);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        z-index: 2;
    }
    
    /* Satellite styles */
    .satellite {
        position: absolute;
        width: 24px;
        height: 12px;
        background-color: #f5f5f5;
        border-radius: 2px;
        left: 50%;
        top: 50%;
        transform-origin: center center;
        animation: orbit-satellite 8s linear infinite;
        z-index: 3;
    }
    
    /* Satellite solar panels */
    .satellite:before, .satellite:after {
        content: '';
        position: absolute;
        width: 18px;
        height: 4px;
        background-color: #ff9800;
        top: 4px;
    }
    
    .satellite:before {
        left: -18px;
    }
    
    .satellite:after {
        right: -18px;
    }
    
    @keyframes orbit-satellite {
        0% {
            transform: translate(-50%, -50%) rotate(0deg) translateX(60px) rotate(0deg);
        }
        100% {
            transform: translate(-50%, -50%) rotate(360deg) translateX(60px) rotate(-360deg);
        }
    }
    
    /* Shooting star */
    .shooting-star {
        position: absolute;
        width: 4px;
        height: 4px;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 50%, rgba(255,255,255,0) 100%);
        border-radius: 50%;
        opacity: 0;
        top: 20%;
        left: 20%;
        animation: shooting 4s linear infinite;
        transform: rotate(45deg);
    }
    
    @keyframes shooting {
        0% {
            transform: translateX(0) translateY(0) rotate(45deg) scale(1);
            opacity: 0;
        }
        5% {
            opacity: 1;
        }
        20% {
            transform: translateX(120px) translateY(120px) rotate(45deg) scale(0.2);
            opacity: 0;
        }
        100% {
            transform: translateX(120px) translateY(120px) rotate(45deg) scale(0.2);
            opacity: 0;
        }
    }
    
    /* Loading message */
    .loading-message {
        position: relative;
        color: white;
        font-weight: bold;
        margin-top: 100px;
        z-index: 5;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
    """, unsafe_allow_html=True)

# Add the CSS
add_satellite_css()

# Function to display satellite loading animation
def satellite_loading(message="Loading satellite data..."):
    # Generate 10 random stars for the background
    stars_html = ""
    for _ in range(10):
        # Random position and size for each star
        left = random.randint(5, 95)
        top = random.randint(5, 95)
        size = random.randint(1, 3)
        delay = random.randint(0, 20) / 10  # Random delay for twinkling
        
        stars_html += f"""
        <div class="star" style="left: {left}%; top: {top}%; width: {size}px; height: {size}px; 
        animation-delay: {delay}s"></div>
        """
    
    return st.markdown(f"""
    <div class="satellite-container">
        <div class="space-background">
            {stars_html}
            <div class="planet"></div>
            <div class="planet-rings"></div>
            <div class="satellite"></div>
            <div class="shooting-star"></div>
        </div>
        <div class="loading-message">{message}</div>
    </div>
    """, unsafe_allow_html=True)

# Custom spinner replacement
def satellite_spinner(text="Loading satellite data..."):
    # Create a placeholder for our custom animation
    placeholder = st.empty()
    
    # This creates a decorator-like context manager
    class SatelliteSpinnerContextManager:
        def __init__(self, text, placeholder):
            self.text = text
            self.placeholder = placeholder
            
        def __enter__(self):
            # Generate random stars for the background
            stars_html = ""
            for _ in range(10):
                # Random position and size for each star
                left = random.randint(5, 95)
                top = random.randint(5, 95)
                size = random.randint(1, 3)
                delay = random.randint(0, 20) / 10  # Random delay for twinkling
                
                stars_html += f"""
                <div class="star" style="left: {left}%; top: {top}%; width: {size}px; height: {size}px; 
                animation-delay: {delay}s"></div>
                """
            
            # Show the animation
            self.placeholder.markdown(f"""
            <div class="satellite-container">
                <div class="space-background">
                    {stars_html}
                    <div class="planet"></div>
                    <div class="planet-rings"></div>
                    <div class="satellite"></div>
                    <div class="shooting-star"></div>
                </div>
                <div class="loading-message">{self.text}</div>
            </div>
            """, unsafe_allow_html=True)
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Clear the animation
            self.placeholder.empty()
            
    return SatelliteSpinnerContextManager(text, placeholder)

# Main title
st.title("Satellite Trajectory Analysis Dashboard")

# Add tabs for different data categories at the top of the app
data_category = st.radio(
    "Select Data Category",
    ["Trajectories", "Satellite Catalog", "Launch Sites", "Decay Data", "Conjunction Data", "Boxscore Data"],
    horizontal=True,
    help="Choose which type of space data to explore"
)

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

# Connect to database (needed for all data categories)
try:
    engine = db.get_database_connection()
except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")
    st.stop()

# Only show satellite filters for Trajectories category
if data_category != "Trajectories":
    # For other data categories, the filters are handled within each category's section
    pass
else:
    # Show the satellite trajectory filters
    try:
        # Get available satellites with names
        satellites_dict = db.get_satellites(engine)
        
        if not satellites_dict:
            st.warning("No satellite data found. Make sure Space-Track.org credentials are set.")
            st.stop()
            
    except Exception as e:
        st.error(f"Error retrieving satellite data: {str(e)}")
        st.stop()

    # Display source of the data
    if has_space_track_credentials:
        st.sidebar.success("Using real-time data from Space-Track.org")
    else:
        st.sidebar.info("Using locally cached satellite data")

    # Format satellite names for display
    satellite_options = [f"{name} (ID: {sat_id})" for sat_id, name in satellites_dict.items()]
    id_to_display_name = {sat_id: f"{name} (ID: {sat_id})" for sat_id, name in satellites_dict.items()}
    display_name_to_id = {f"{name} (ID: {sat_id})": sat_id for sat_id, name in satellites_dict.items()}

    # Satellite selection
    selected_satellite_display = st.sidebar.selectbox(
        "Select Satellite",
        options=satellite_options,
        help="Choose a satellite to view its trajectory data"
    )

    # Extract the actual satellite ID from the selection
    selected_satellite = display_name_to_id[selected_satellite_display]

    # Store the display name for later use
    st.session_state['selected_satellite_name'] = selected_satellite_display

    # Time period selection
    st.sidebar.subheader("Time Period")
    today = datetime.now()

    # Set appropriate date ranges based on satellite selection
    # Extract launch date if available in satellite name
    launch_date_match = None
    if "selected_satellite_name" in st.session_state:
        satellite_name = st.session_state["selected_satellite_name"]
        if "Launched:" in satellite_name:
            try:
                launch_str = satellite_name.split("Launched:")[1].strip()
                launch_date_str = launch_str.strip("() ")
                launch_date_match = pd.to_datetime(launch_date_str)
            except:
                pass

    # Set default dates based on selected satellite
    if launch_date_match:
        # If we have a launch date, suggest a period after launch
        # If it's an old satellite, just show last week
        if (today - launch_date_match).days > 30:
            default_start_date = today - timedelta(days=7)
            date_suggestion = "Showing data for the past week"
        else:
            # For recently launched satellites, show from launch date
            default_start_date = launch_date_match
            date_suggestion = f"Showing data since launch date: {launch_date_match.strftime('%Y-%m-%d')}"
    else:
        # Default to last week if no launch date available
        default_start_date = today - timedelta(days=7)
        date_suggestion = "Showing data for the past week"

    # Display date suggestion
    st.sidebar.info(date_suggestion)

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
        # Show our custom satellite loading animation instead of the default spinner
        with satellite_spinner(f"Loading trajectory data for satellite {selected_satellite}..."):
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
    if 'selected_satellite_name' in st.session_state:
        st.subheader(f"Satellite: {st.session_state['selected_satellite_name']}")
    elif 'satellite_name' in st.session_state:
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
        # Get start and end dates from the data itself if not defined in current scope
        try:
            if 'timestamp' in df.columns:
                data_start_date = pd.to_datetime(df['timestamp'].min()).strftime("%Y-%m-%d")
                data_end_date = pd.to_datetime(df['timestamp'].max()).strftime("%Y-%m-%d")
            else:
                data_start_date = "unknown_start"
                data_end_date = "unknown_end"
            
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"satellite_{satellite_id}_trajectory_{data_start_date}_{data_end_date}.csv",
                mime="text/csv",
            )
        except:
            # Fallback without dates if there's an error
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"satellite_{satellite_id}_trajectory.csv",
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
            # Check if we have altitude data
            if 'altitude' not in df.columns:
                # Calculate it from x, y, z if needed
                if all(col in df.columns for col in ['x', 'y', 'z']):
                    df['altitude'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2) - 6371000  # Earth radius in meters
                    st.info("Altitude was calculated from positional coordinates")
            
            # Print debugging info
            st.write(f"Data points: {len(df)}")
            st.write(f"Columns available: {', '.join(df.columns)}")
            
            # Create the plot
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
    # Show appropriate content based on selected data category
    if data_category == "Trajectories":
        # Display instructions if no data is loaded
        st.info("👈 Select a satellite and time period, then click 'Load Data' to begin.")
        
        # Show sample information about the trajectory analysis
        st.write("""
        ## Satellite Trajectory Analysis
        
        This view provides tools for analyzing satellite trajectory data from the Combined Space Operations Center (CSpOC).
        
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
    else:
        # Handle other data categories
        st.sidebar.info(f"Loading {data_category} information...")
        
        # Configure sidebar for each data category
        if data_category == "Satellite Catalog":
            st.sidebar.subheader("Catalog Filters")
            limit = st.sidebar.slider("Number of records", 10, 500, 100)
            
            if st.sidebar.button("Load Catalog Data"):
                with satellite_spinner(f"Loading satellite catalog data..."):
                    try:
                        data = db.get_space_track_data(engine, "catalog", limit=limit)
                        if not data.empty:
                            st.session_state['catalog_data'] = data
                        else:
                            st.warning("No catalog data found. Make sure Space-Track.org credentials are valid.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                    except Exception as e:
                        st.error(f"Error retrieving catalog data: {str(e)}")
            
            if 'catalog_data' in st.session_state:
                st.subheader("Satellite Catalog Information")
                
                # Displaying the data
                data = st.session_state['catalog_data']
                
                # Column selection
                all_columns = data.columns.tolist()
                default_columns = ['NORAD_CAT_ID', 'SATNAME', 'OBJECT_TYPE', 'COUNTRY', 'LAUNCH_DATE', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE']
                selected_columns = st.multiselect(
                    "Select columns to display",
                    options=all_columns,
                    default=[col for col in default_columns if col in all_columns]
                )
                
                # Filter by country if column exists
                if 'COUNTRY' in data.columns:
                    countries = sorted(data['COUNTRY'].unique())
                    selected_countries = st.multiselect(
                        "Filter by Country",
                        options=countries,
                        default=[]
                    )
                    
                    if selected_countries:
                        data = data[data['COUNTRY'].isin(selected_countries)]
                
                # Add live filtering options for the dataframe
                st.write("### Live Data Filtering")
                with st.expander("Filter Data", expanded=False):
                    # Create a container with custom styling
                    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                    
                    # Add search functionality for each column
                    filter_cols = st.columns(3)
                    
                    # Track if we have applied any filters
                    filters_applied = False
                    filtered_data = data.copy()
                    
                    with filter_cols[0]:
                        # Text search filter for satellite name
                        if 'SATNAME' in data.columns:
                            name_filter = st.text_input("Filter by Satellite Name", 
                                                      placeholder="e.g., ISS, STARLINK")
                            if name_filter:
                                filtered_data = filtered_data[filtered_data['SATNAME'].str.contains(name_filter, case=False, na=False)]
                                filters_applied = True
                                
                    with filter_cols[1]:
                        # Object type filter (dropdown)
                        if 'OBJECT_TYPE' in data.columns:
                            object_types = ['All'] + sorted(data['OBJECT_TYPE'].dropna().unique().tolist())
                            selected_type = st.selectbox("Filter by Object Type", object_types)
                            if selected_type != 'All':
                                filtered_data = filtered_data[filtered_data['OBJECT_TYPE'] == selected_type]
                                filters_applied = True
                                
                    with filter_cols[2]:
                        # Country filter (dropdown)
                        if 'COUNTRY' in data.columns:
                            countries = ['All'] + sorted(data['COUNTRY'].dropna().unique().tolist())
                            selected_country = st.selectbox("Filter by Country", countries)
                            if selected_country != 'All':
                                filtered_data = filtered_data[filtered_data['COUNTRY'] == selected_country]
                                filters_applied = True
                    
                    # Add more specific filters in another row
                    filter_cols2 = st.columns(3)
                    
                    with filter_cols2[0]:
                        # Launch year range
                        if 'LAUNCH_DATE' in data.columns or 'LAUNCH_YEAR' in data.columns:
                            year_col = 'LAUNCH_YEAR' if 'LAUNCH_YEAR' in data.columns else 'LAUNCH_DATE'
                            
                            # Convert to numeric or extract year from date
                            if year_col == 'LAUNCH_DATE':
                                # Try to convert to datetime and extract year
                                try:
                                    years = pd.to_datetime(data[year_col], errors='coerce').dt.year.dropna().astype(int)
                                except:
                                    years = []
                            else:
                                # Direct numeric conversion
                                years = pd.to_numeric(data[year_col], errors='coerce').dropna().astype(int)
                            
                            if len(years) > 0:
                                min_year, max_year = int(min(years)), int(max(years))
                                year_range = st.slider("Launch Year Range", min_year, max_year, (min_year, max_year))
                                
                                if year_range != (min_year, max_year):
                                    if year_col == 'LAUNCH_DATE':
                                        # Filter by year component of date
                                        filtered_data = filtered_data[
                                            pd.to_datetime(filtered_data[year_col], errors='coerce').dt.year.between(
                                                year_range[0], year_range[1]
                                            )
                                        ]
                                    else:
                                        # Direct numeric comparison
                                        filtered_data = filtered_data[
                                            pd.to_numeric(filtered_data[year_col], errors='coerce').between(
                                                year_range[0], year_range[1]
                                            )
                                        ]
                                    filters_applied = True
                    
                    with filter_cols2[1]:
                        # Orbital period range
                        if 'PERIOD' in data.columns:
                            try:
                                periods = pd.to_numeric(data['PERIOD'], errors='coerce').dropna()
                                if len(periods) > 0:
                                    min_period, max_period = float(min(periods)), float(max(periods))
                                    period_range = st.slider("Orbital Period (minutes)", 
                                                           min_period, max_period, 
                                                           (min_period, max_period),
                                                           step=10.0)
                                    
                                    if period_range != (min_period, max_period):
                                        filtered_data = filtered_data[
                                            pd.to_numeric(filtered_data['PERIOD'], errors='coerce').between(
                                                period_range[0], period_range[1]
                                            )
                                        ]
                                        filters_applied = True
                            except:
                                pass
                    
                    with filter_cols2[2]:
                        # Current objects only checkbox
                        if 'CURRENT' in data.columns:
                            current_only = st.checkbox("Show Current Objects Only")
                            if current_only:
                                filtered_data = filtered_data[filtered_data['CURRENT'] == 'Y']
                                filters_applied = True
                    
                    # Filter stats and reset button
                    cols = st.columns([3, 1])
                    with cols[0]:
                        if filters_applied:
                            st.info(f"Showing {len(filtered_data)} of {len(data)} records ({len(filtered_data)/len(data):.1%})")
                        else:
                            st.info(f"No filters applied. Showing all {len(data)} records.")
                            
                    with cols[1]:
                        if filters_applied and st.button("Reset Filters"):
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display the filtered data
                display_data = filtered_data if filters_applied else data
                
                if selected_columns:
                    st.dataframe(display_data[selected_columns], use_container_width=True)
                else:
                    st.dataframe(display_data, use_container_width=True)
                
                # Add field explanations in an expandable section
                with st.expander("Satellite Catalog Fields Explanation"):
                    st.markdown("""
                    | Field | Description |
                    | --- | --- |
                    | NORAD_CAT_ID | The unique identifier assigned by NORAD (North American Aerospace Defense Command) |
                    | SATNAME | Official name of the satellite |
                    | OBJECT_TYPE | Classification of the object (Payload, Rocket Body, Debris, etc.) |
                    | COUNTRY | Country or organization responsible for the satellite |
                    | LAUNCH_DATE | Date when the satellite was launched |
                    | SITE | Launch site location |
                    | DECAY_DATE | Date when the satellite re-entered Earth's atmosphere (if applicable) |
                    | PERIOD | Orbital period in minutes (time to complete one orbit) |
                    | INCLINATION | Orbital inclination in degrees (angle between orbital plane and equator) |
                    | APOGEE | Highest altitude of the satellite in kilometers |
                    | PERIGEE | Lowest altitude of the satellite in kilometers |
                    | RCS | Radar Cross Section - measure of how detectable the object is by radar |
                    | LAUNCH_YEAR | Year of launch |
                    | LAUNCH_NUM | Launch number for that year |
                    | LAUNCH_PIECE | Letter designating piece of launch (A=primary payload) |
                    | CURRENT | Indicates if the object is still in orbit (Y/N) |
                    | OBJECT_ID | International designator in format YYYY-NNNLPP (year, launch number, piece) |
                    """)
                
                # Statistics about the catalog
                st.subheader("Satellite Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'OBJECT_TYPE' in data.columns:
                        st.write("### Objects by Type")
                        type_counts = data['OBJECT_TYPE'].value_counts().reset_index()
                        type_counts.columns = ['Object Type', 'Count']
                        fig = px.pie(type_counts, values='Count', names='Object Type', title='Distribution by Object Type')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'COUNTRY' in data.columns:
                        st.write("### Objects by Country")
                        country_counts = data['COUNTRY'].value_counts().head(10).reset_index()
                        country_counts.columns = ['Country', 'Count']
                        fig = px.bar(country_counts, x='Country', y='Count', title='Top 10 Countries by Object Count')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Allow CSV download
                csv = utils.convert_df_to_csv(data)
                st.download_button(
                    label="Download catalog data as CSV",
                    data=csv,
                    file_name=f"satellite_catalog.csv",
                    mime="text/csv",
                )
            
            else:
                st.info("Click 'Load Catalog Data' to view satellite catalog information")
                
        elif data_category == "Launch Sites":
            if st.sidebar.button("Load Launch Sites Data"):
                with satellite_spinner("Loading launch sites data..."):
                    try:
                        data = db.get_space_track_data(engine, "launch_sites")
                        if not data.empty:
                            st.session_state['launch_sites_data'] = data
                        else:
                            st.warning("No launch sites data found. Make sure Space-Track.org credentials are valid.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                    except Exception as e:
                        st.error(f"Error retrieving launch sites data: {str(e)}")
            
            if 'launch_sites_data' in st.session_state:
                st.subheader("Launch Sites Information")
                
                # Display the data
                data = st.session_state['launch_sites_data']
                st.dataframe(data, use_container_width=True)
                
                # Add field explanations in an expandable section
                with st.expander("Launch Sites Fields Explanation"):
                    st.markdown("""
                    | Field | Description |
                    | --- | --- |
                    | SITE_CODE | Unique identifier for the launch site |
                    | SITE_NAME | Full name of the launch facility |
                    | LAUNCH_SITE | Description of the site and facilities |
                    | COUNTRY | Country where the launch site is located |
                    | LONGITUDE | Geographical longitude coordinate (degrees) |
                    | LATITUDE | Geographical latitude coordinate (degrees) |
                    | ALTITUDE | Height above sea level (meters) |
                    | FIRST_LAUNCH | Date of the first launch from this site |
                    | LAST_LAUNCH | Date of the most recent launch from this site |
                    | TOTAL_LAUNCHES | Total number of launches conducted from this site |
                    | LAUNCH_VEHICLES | Types of launch vehicles used at this site |
                    | STATUS | Current operational status of the launch site |
                    """)
                
                # Map of launch sites if coordinates are available
                if 'LATITUDE' in data.columns and 'LONGITUDE' in data.columns:
                    st.subheader("Launch Sites Map")
                    
                    # Create a map
                    map_data = data.dropna(subset=['LATITUDE', 'LONGITUDE']).copy()
                    
                    if not map_data.empty:
                        # Convert coordinates to numeric
                        map_data['LATITUDE'] = pd.to_numeric(map_data['LATITUDE'], errors='coerce')
                        map_data['LONGITUDE'] = pd.to_numeric(map_data['LONGITUDE'], errors='coerce')
                        
                        # Drop any rows with non-numeric coordinates
                        map_data = map_data.dropna(subset=['LATITUDE', 'LONGITUDE'])
                        
                        if not map_data.empty:
                            # Create a scatter mapbox
                            fig = px.scatter_mapbox(
                                map_data,
                                lat='LATITUDE',
                                lon='LONGITUDE',
                                hover_name='SITE_NAME',
                                hover_data=['SITE_CODE', 'COUNTRY'],
                                zoom=1
                            )
                            fig.update_layout(mapbox_style="open-street-map")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No valid coordinate data for mapping launch sites.")
                    else:
                        st.warning("No coordinate data available for launch sites.")
                
                # Allow CSV download
                csv = utils.convert_df_to_csv(data)
                st.download_button(
                    label="Download launch sites data as CSV",
                    data=csv,
                    file_name="launch_sites.csv",
                    mime="text/csv",
                )
            
            else:
                st.info("Click 'Load Launch Sites Data' to view launch site information")
                
        elif data_category == "Decay Data":
            st.sidebar.subheader("Decay Data Filters")
            days_back = st.sidebar.slider("Days to look back", 7, 365, 30)
            limit = st.sidebar.slider("Number of records", 10, 500, 100)
            
            if st.sidebar.button("Load Decay Data"):
                with satellite_spinner("Loading decay data..."):
                    # Add a status container to show the current operation
                    status_container = st.empty()
                    status_container.info("Connecting to Space-Track.org to retrieve decay data... This might take a moment as we try multiple API endpoints.")
                    
                    try:
                        # Wrap this in a try-except to handle potential API errors
                        data = db.get_space_track_data(engine, "decay", days_back=days_back, limit=limit)
                        
                        if not data.empty:
                            # Data loaded successfully
                            status_container.success(f"Successfully retrieved {len(data)} decay records!")
                            st.session_state['decay_data'] = data
                        else:
                            # No data found
                            status_container.warning("No decay data retrieved from Space-Track.org")
                            st.warning("No decay data found. This could be due to one of the following reasons:")
                            st.markdown("""
                            - Your Space-Track.org credentials might not have access to decay data
                            - The Space-Track API structure may have changed
                            - There might not be any decay data in the selected time period
                            - The service might be temporarily unavailable
                            """)
                            
                            if not has_space_track_credentials:
                                st.error("Space-Track.org credentials are required to access this data. Please set SPACETRACK_USERNAME and SPACETRACK_PASSWORD in your environment.")
                            
                            # Provide a link to Space-Track for manual checking
                            st.markdown("[Check Space-Track.org website directly](https://www.space-track.org)")
                    
                    except Exception as e:
                        error_msg = str(e)
                        status_container.error("Error connecting to Space-Track.org")
                        
                        # Provide more helpful error details
                        if "DOES NOT EXIST FOR TABLE" in error_msg:
                            st.error("API Error: The Space-Track database schema has changed. The column names used in the query are no longer valid.")
                            st.info("The application is designed to try multiple alternative column names automatically.")
                        elif "Unauthorized" in error_msg or "401" in error_msg:
                            st.error("Authentication Error: Space-Track.org credentials are invalid or expired.")
                            st.info("Please check your SPACETRACK_USERNAME and SPACETRACK_PASSWORD environment variables.")
                        elif "Timeout" in error_msg or "timed out" in error_msg.lower():
                            st.error("Timeout Error: Connection to Space-Track.org timed out.")
                            st.info("The service might be experiencing high load or network issues. Try again later.")
                        else:
                            st.error(f"Error retrieving decay data: {error_msg}")
                            
                        # Log the full error details for debugging
                        print(f"Detailed decay data error: {e}")
            
            if 'decay_data' in st.session_state:
                st.subheader("Satellite Decay Information")
                
                # Display the data
                data = st.session_state['decay_data']
                
                # Key columns to display
                if 'DECAY_DATE' in data.columns:
                    # Try to convert to datetime for better sorting
                    try:
                        data['DECAY_DATE'] = pd.to_datetime(data['DECAY_DATE'], errors='coerce')
                    except:
                        pass
                
                st.dataframe(data, use_container_width=True)
                
                # Add field explanations in an expandable section
                with st.expander("Decay Data Fields Explanation"):
                    st.markdown("""
                    | Field | Description |
                    | --- | --- |
                    | NORAD_CAT_ID | The unique identifier assigned by NORAD |
                    | SATNAME | Name of the satellite or space object |
                    | OBJECT_ID | International designator in format YYYY-NNNLPP |
                    | DECAY_DATE | Date and time when the object re-entered Earth's atmosphere |
                    | DECAY_EPOCH | Time of decay in standard epoch format |
                    | SOURCE | Source of the decay determination (observed or predicted) |
                    | MSG_EPOCH | Date when the decay message was generated |
                    | REV_NUMBER | Number of orbits completed before decay |
                    | INCLINATION | Orbital inclination in degrees at time of decay |
                    | APOGEE | Last known highest altitude in kilometers before decay |
                    | PERIGEE | Last known lowest altitude in kilometers before decay |
                    | COMMENT | Additional information about the re-entry event |
                    | RCS | Radar Cross Section - size of the object |
                    | ORBIT_CENTER | Center of orbit (typically EARTH) |
                    | COUNTRY | Country or organization that owned/operated the object |
                    """)
                
                # Create visualization of decay dates
                if 'DECAY_DATE' in data.columns:
                    st.subheader("Recent Re-entries")
                    
                    # Time series of decays
                    decay_dates = pd.to_datetime(data['DECAY_DATE'], errors='coerce')
                    if not decay_dates.isna().all():
                        daily_counts = decay_dates.dt.date.value_counts().sort_index()
                        daily_counts = daily_counts.reset_index()
                        daily_counts.columns = ['Date', 'Count']
                        
                        fig = px.line(
                            daily_counts, 
                            x='Date', 
                            y='Count',
                            title='Objects Re-entering Earth\'s Atmosphere by Date',
                            labels={'Count': 'Number of Objects', 'Date': 'Re-entry Date'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No valid decay date information available for visualization.")
                
                # Allow CSV download
                csv = utils.convert_df_to_csv(data)
                st.download_button(
                    label="Download decay data as CSV",
                    data=csv,
                    file_name="satellite_decay_data.csv",
                    mime="text/csv",
                )
            
            else:
                st.info("Click 'Load Decay Data' to view satellite decay information")
                
        elif data_category == "Conjunction Data":
            st.sidebar.subheader("Conjunction Data Filters")
            days_back = st.sidebar.slider("Days to look back", 1, 30, 7)
            limit = st.sidebar.slider("Number of records", 10, 500, 100)
            
            if st.sidebar.button("Load Conjunction Data"):
                with satellite_spinner("Loading conjunction data..."):
                    try:
                        # Display info about multiple endpoint attempts
                        status_container = st.empty()
                        status_container.info("Attempting to connect to Space-Track.org conjunction data. This may take a moment as we try multiple API endpoints...")
                        
                        # Get the data
                        data = db.get_space_track_data(engine, "conjunction", days_back=days_back, limit=limit)
                        
                        # Update status based on result
                        if not data.empty:
                            status_container.success("Successfully retrieved conjunction data!")
                            st.session_state['conjunction_data'] = data
                        else:
                            status_container.warning("No conjunction data found. The application tried multiple API endpoints, but none returned data.")
                            st.expander("Troubleshooting Information", expanded=True).markdown("""
                            ### Possible Reasons for Missing Conjunction Data
                            1. **API Access Permissions**: Your Space-Track.org account may not have access to conjunction data
                            2. **API Changes**: Space-Track has recently restructured their API endpoints
                            3. **No Recent Conjunctions**: There may be no conjunction events in the selected time period
                            
                            ### Solutions
                            - Try selecting a different data category from the sidebar
                            - Ensure you have the correct Space-Track.org credentials with appropriate access levels
                            - Contact Space-Track.org support to request access to conjunction data endpoints
                            """)
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                            else:
                                st.info("Try refreshing or selecting a different data category.")
                    except Exception as e:
                        st.error(f"Error retrieving conjunction data: {str(e)}")
                        if "basicspacedata_cdm_public" in str(e) or "NOT EXIST FOR TABLE" in str(e):
                            st.warning("The Space-Track API endpoint structure has changed. The application will try multiple alternative endpoints automatically.")
                            # Try once more with the enhanced fallback system
                            try:
                                status_container = st.empty()
                                status_container.info("Retrying with advanced fallback system...")
                                
                                # Get the data with enhanced fallbacks
                                data = db.get_space_track_data(engine, "conjunction", days_back=days_back, limit=limit)
                                
                                if not data.empty:
                                    status_container.success("Successfully retrieved conjunction data with fallback system!")
                                    st.session_state['conjunction_data'] = data
                                else:
                                    status_container.warning("All fallback attempts failed to retrieve conjunction data.")
                            except Exception as retry_error:
                                st.error(f"Fallback system also failed: {str(retry_error)}")
                        
                        st.expander("Technical Details", expanded=False).code(str(e))
                        st.info("Please try a different data category or contact Space-Track.org support for more information about conjunction data access.")
            
            if 'conjunction_data' in st.session_state:
                st.subheader("Conjunction Data Messages (Close Approaches)")
                
                # Display the data
                data = st.session_state['conjunction_data']
                
                # Check if we have enough data for meaningful analysis
                if data.empty:
                    st.warning("The conjunction data returned is empty. Try a different data category.")
                else:
                    # Add live filtering options for conjunction data
                    st.write("### Live Conjunction Data Filtering")
                    with st.expander("Filter Conjunction Data", expanded=False):
                        # Create a container with custom styling
                        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                        
                        # Add search functionality for each column
                        filter_cols = st.columns(3)
                        
                        # Track if we have applied any filters
                        filters_applied = False
                        filtered_data = data.copy()
                        
                        with filter_cols[0]:
                            # Filter by object name
                            # Identify all possible name columns for primary object
                            obj_name_cols = [col for col in data.columns if any(x in col.upper() for x in ['OBJECT', 'NAME', 'SAT_1'])]
                            
                            if obj_name_cols:
                                # Debug output - uncomment if needed
                                # st.write(f"Available object name columns: {obj_name_cols}")
                                
                                name_filter = st.text_input("Filter by Primary Object", 
                                                            placeholder="e.g., ISS, COSMOS")
                                
                                if name_filter:
                                    # Initialize mask as all False
                                    mask = pd.Series(False, index=filtered_data.index)
                                    
                                    # Try to match across all name columns (more robust)
                                    for col in obj_name_cols:
                                        if col in data.columns:
                                            try:
                                                # Convert column to string and check for case-insensitive matches
                                                col_mask = filtered_data[col].astype(str).str.contains(
                                                    name_filter, case=False, na=False, regex=True
                                                )
                                                # Combine with OR logic - match in any column is sufficient
                                                mask = mask | col_mask
                                                # Debug output - uncomment if needed
                                                # st.write(f"Found {col_mask.sum()} matches in column {col}")
                                            except Exception as e:
                                                st.warning(f"Error filtering by {col}: {e}")
                                    
                                    # Apply the combined mask
                                    if mask.any():
                                        filtered_data = filtered_data[mask]
                                        filters_applied = True
                                        st.success(f"Found {mask.sum()} matching objects containing '{name_filter}'")
                                    else:
                                        st.warning(f"No matches found for '{name_filter}' in any name column")
                            
                        with filter_cols[1]:
                            # Filter by secondary object
                            obj2_name_cols = [col for col in data.columns if any(x in col.upper() for x in ['OBJECT_2', 'SAT_2', 'SECOND'])]
                            
                            if obj2_name_cols:
                                # Debug output - uncomment if needed
                                # st.write(f"Available secondary object columns: {obj2_name_cols}")
                                
                                name2_filter = st.text_input("Filter by Secondary Object", 
                                                           placeholder="e.g., DEBRIS, STARLINK")
                                
                                if name2_filter:
                                    # Initialize mask as all False
                                    mask2 = pd.Series(False, index=filtered_data.index)
                                    
                                    # Try to match across all secondary object name columns
                                    for col in obj2_name_cols:
                                        if col in data.columns:
                                            try:
                                                # Convert column to string and check for case-insensitive matches
                                                col_mask = filtered_data[col].astype(str).str.contains(
                                                    name2_filter, case=False, na=False, regex=True
                                                )
                                                # Combine with OR logic - match in any column is sufficient
                                                mask2 = mask2 | col_mask
                                                # Debug output - uncomment if needed
                                                # st.write(f"Found {col_mask.sum()} matches in column {col}")
                                            except Exception as e:
                                                st.warning(f"Error filtering by {col}: {e}")
                                    
                                    # Apply the combined mask
                                    if mask2.any():
                                        filtered_data = filtered_data[mask2]
                                        filters_applied = True
                                        st.success(f"Found {mask2.sum()} matching secondary objects containing '{name2_filter}'")
                                    else:
                                        st.warning(f"No matches found for '{name2_filter}' in any secondary object column")
                        
                        with filter_cols[2]:
                            # Date range filter
                            date_cols = [col for col in data.columns if any(x in col.upper() for x in ['DATE', 'TIME', 'TCA'])]
                            if date_cols:
                                date_col = date_cols[0]
                                
                                try:
                                    # Try to convert to datetime
                                    date_series = pd.to_datetime(data[date_col], errors='coerce')
                                    valid_dates = date_series.dropna()
                                    
                                    if not valid_dates.empty:
                                        date_min = valid_dates.min().date()
                                        date_max = valid_dates.max().date()
                                        
                                        date_range = st.date_input(
                                            "Date Range",
                                            value=(date_min, date_max),
                                            min_value=date_min,
                                            max_value=date_max
                                        )
                                        
                                        if len(date_range) == 2:
                                            start_date, end_date = date_range
                                            if start_date != date_min or end_date != date_max:
                                                filtered_data = filtered_data[
                                                    (pd.to_datetime(filtered_data[date_col], errors='coerce').dt.date >= start_date) & 
                                                    (pd.to_datetime(filtered_data[date_col], errors='coerce').dt.date <= end_date)
                                                ]
                                                filters_applied = True
                                except Exception as e:
                                    st.warning(f"Could not process dates in {date_col} column: {e}")
                        
                        # Add risk-based filters
                        filter_cols2 = st.columns(3)
                        
                        with filter_cols2[0]:
                            # Miss distance filter
                            miss_dist_cols = [col for col in data.columns if any(term in col.upper() for term in ['MISS', 'DIST', 'RANGE', 'RNG'])]
                            if miss_dist_cols:
                                miss_dist_col = miss_dist_cols[0]
                                
                                try:
                                    miss_dist_vals = pd.to_numeric(data[miss_dist_col], errors='coerce').dropna()
                                    if not miss_dist_vals.empty:
                                        min_dist = float(miss_dist_vals.min())
                                        max_dist = float(miss_dist_vals.max())
                                        
                                        # Ensure min and max are not the same value
                                        if min_dist == max_dist:
                                            max_dist = min_dist + 0.1
                                            
                                        # Make sure step is appropriate
                                        step_size = max(0.001, (max_dist-min_dist)/100)
                                        
                                        # Show the current range
                                        st.write(f"Range: {min_dist:.3f} km to {max_dist:.3f} km")
                                        
                                        # Use a range slider instead if values differ enough
                                        if max_dist - min_dist > step_size * 2:
                                            miss_dist_range = st.slider(
                                                "Miss Distance (km)",
                                                min_value=min_dist,
                                                max_value=max_dist,
                                                value=(min_dist, max_dist),
                                                step=step_size
                                            )
                                        else:
                                            # If range is too small, just show a message
                                            st.info("Miss distance range is too small to filter")
                                            miss_dist_range = (min_dist, max_dist)
                                        
                                        if miss_dist_range != (min_dist, max_dist):
                                            filtered_data = filtered_data[
                                                pd.to_numeric(filtered_data[miss_dist_col], errors='coerce').between(
                                                    miss_dist_range[0], miss_dist_range[1]
                                                )
                                            ]
                                            filters_applied = True
                                except Exception as e:
                                    st.warning(f"Could not filter by miss distance: {e}")
                        
                        with filter_cols2[1]:
                            # Probability filter (if available)
                            prob_cols = [col for col in data.columns if any(term in col.upper() for term in ['PC', 'PROB', 'COLLISION'])]
                            if prob_cols:
                                prob_col = prob_cols[0]
                                
                                try:
                                    prob_vals = pd.to_numeric(data[prob_col], errors='coerce').dropna()
                                    if not prob_vals.empty:
                                        min_prob = float(prob_vals.min())
                                        max_prob = float(prob_vals.max())
                                        
                                        # Use scientific notation for very small values
                                        if min_prob < 0.00001:
                                            min_prob_disp = f"{min_prob:.2e}"
                                        else:
                                            min_prob_disp = f"{min_prob:.6f}"
                                            
                                        if max_prob < 0.00001:
                                            max_prob_disp = f"{max_prob:.2e}"
                                        else:
                                            max_prob_disp = f"{max_prob:.6f}"
                                        
                                        st.markdown(f"Collision Probability Range:  \n{min_prob_disp} to {max_prob_disp}")
                                        
                                        # Instead of using a log slider which can cause issues, 
                                        # just use probability filter categories
                                        import numpy as np
                                        
                                        # Create probability categories for easier filtering
                                        prob_categories = {
                                            "All probabilities": (min_prob, max_prob),
                                            "Negligible (<1e-6)": (0, 1e-6),
                                            "Very Low (1e-6 to 1e-5)": (1e-6, 1e-5),
                                            "Low (1e-5 to 1e-4)": (1e-5, 1e-4),
                                            "Medium (1e-4 to 1e-3)": (1e-4, 1e-3),
                                            "High (1e-3 to 1e-2)": (1e-3, 1e-2),
                                            "Very High (>1e-2)": (1e-2, max(max_prob, 1.0))
                                        }
                                        
                                        selected_category = st.selectbox(
                                            "Filter by Collision Probability Level",
                                            options=list(prob_categories.keys())
                                        )
                                        
                                        # Set the probability range based on selected category
                                        prob_range = prob_categories[selected_category]
                                        
                                        # Only update filter if not "All probabilities"
                                        if selected_category != "All probabilities":
                                            filtered_data = filtered_data[
                                                pd.to_numeric(filtered_data[prob_col], errors='coerce').between(
                                                    prob_range[0], prob_range[1]
                                                )
                                            ]
                                            filters_applied = True
                                except Exception as e:
                                    st.warning(f"Could not filter by probability: {e}")
                        
                        with filter_cols2[2]:
                            # Relative velocity filter
                            vel_cols = [col for col in data.columns if any(term in col.upper() for term in ['SPEED', 'VEL', 'V_REL'])]
                            if vel_cols:
                                vel_col = vel_cols[0]
                                
                                try:
                                    vel_vals = pd.to_numeric(data[vel_col], errors='coerce').dropna()
                                    if not vel_vals.empty:
                                        min_vel = float(vel_vals.min())
                                        max_vel = float(vel_vals.max())
                                        
                                        # Ensure min and max are not the same value
                                        if min_vel == max_vel:
                                            max_vel = min_vel + 0.1
                                            
                                        # Make sure step is appropriate 
                                        step_size = max(0.1, (max_vel-min_vel)/100)
                                        
                                        # Show the current range
                                        st.write(f"Range: {min_vel:.2f} km/s to {max_vel:.2f} km/s")
                                        
                                        # Use a range slider if values differ enough
                                        if max_vel - min_vel > step_size * 2:
                                            vel_range = st.slider(
                                                "Relative Velocity (km/s)",
                                                min_value=min_vel,
                                                max_value=max_vel,
                                                value=(min_vel, max_vel),
                                                step=step_size
                                            )
                                        else:
                                            # If range is too small, just show a message
                                            st.info("Velocity range is too small to filter")
                                            vel_range = (min_vel, max_vel)
                                        
                                        if vel_range != (min_vel, max_vel):
                                            filtered_data = filtered_data[
                                                pd.to_numeric(filtered_data[vel_col], errors='coerce').between(
                                                    vel_range[0], vel_range[1]
                                                )
                                            ]
                                            filters_applied = True
                                except Exception as e:
                                    st.warning(f"Could not filter by velocity: {e}")
                        
                        # Filter stats and reset button
                        cols = st.columns([3, 1])
                        with cols[0]:
                            if filters_applied:
                                st.info(f"Showing {len(filtered_data)} of {len(data)} conjunction events ({len(filtered_data)/len(data):.1%})")
                            else:
                                st.info(f"No filters applied. Showing all {len(data)} conjunction events.")
                                
                        with cols[1]:
                            if filters_applied and st.button("Reset Filters", key="reset_conj"):
                                st.rerun()
                                
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display the filtered data
                    display_data = filtered_data if filters_applied else data
                    st.dataframe(display_data, use_container_width=True)
                    
                    # Add field explanations in an expandable section
                    with st.expander("Conjunction Data Fields Explanation"):
                        st.markdown("""
                        | Field | Description |
                        | --- | --- |
                        | CDM_ID | Unique identifier for this Conjunction Data Message |
                        | CREATED | Date and time when the conjunction message was created |
                        | TCA / CDM_TCA | Time of Closest Approach - when objects will pass closest to each other |
                        | MISS_DISTANCE | Predicted minimum distance between the two objects in kilometers |
                        | PC | Probability of Collision - likelihood of objects colliding |
                        | EMERGENCY_REPORTABLE | Whether this conjunction requires emergency reporting (Y/N) |
                        | SAT_1_ID / OBJECT_DESIGNATOR | Identifier for the primary object in conjunction |
                        | SAT_1_NAME / OBJECT_NAME | Name of the primary object |
                        | SAT_2_ID / OBJECT_2_DESIGNATOR | Identifier for the secondary object in conjunction |
                        | SAT_2_NAME / OBJECT_2_NAME | Name of the secondary object |
                        | RELATIVE_SPEED | Relative velocity between the two objects in km/s |
                        | RELATIVE_POSITION_R | Radial component of relative position vector |
                        | RELATIVE_POSITION_T | In-track component of relative position vector |
                        | RELATIVE_POSITION_N | Cross-track component of relative position vector |
                        | COLLISION_PROBABILITY | Calculated probability of objects colliding |
                        | COLLISION_RADIUS | Combined radius of both objects in meters |
                        """)
                
                try:
                    # Format the data for better display
                    if 'CDM_TCA' in data.columns:
                        # Try to convert to datetime for better sorting
                        try:
                            data['CDM_TCA'] = pd.to_datetime(data['CDM_TCA'], errors='coerce')
                        except Exception as dt_error:
                            st.warning(f"Could not convert time data: {dt_error}")
                    
                    # Filter conjunction data by minimum probability if available
                    if 'PC' in data.columns:  # Probability of Collision
                        try:
                            data['PC'] = pd.to_numeric(data['PC'], errors='coerce')
                            max_pc = float(data['PC'].max() if not data['PC'].isna().all() else 1.0)
                            min_prob = st.slider(
                                "Minimum Collision Probability", 
                                min_value=0.0, 
                                max_value=max_pc,
                                value=0.0,
                                step=0.0001
                            )
                            data = data[data['PC'] >= min_prob]
                        except Exception as pc_error:
                            st.warning(f"Could not process collision probability data: {pc_error}")
                    
                    # Summary statistics and key insights
                    st.subheader("Conjunction Summary and Key Insights")
                    
                    # Create columns for statistics display
                    stat_col1, stat_col2 = st.columns(2)
                    
                    # Calculate common statistics
                    try:
                        # Count of conjunction events
                        total_events = len(data)
                        
                        with stat_col1:
                            st.metric("Total Conjunction Events", f"{total_events:,}")
                            
                            # Time range
                            if 'CDM_TCA' in data.columns and not data['CDM_TCA'].isna().all():
                                min_date = pd.to_datetime(data['CDM_TCA']).min().strftime('%Y-%m-%d')
                                max_date = pd.to_datetime(data['CDM_TCA']).max().strftime('%Y-%m-%d')
                                st.metric("Date Range", f"{min_date} to {max_date}")
                            
                            # Check for emergency reportable events
                            if 'EMERGENCY_REPORTABLE' in data.columns:
                                emergency_count = data['EMERGENCY_REPORTABLE'].str.upper().str.contains('Y').sum()
                                if emergency_count > 0:
                                    st.metric("Emergency Reportable Events", f"{emergency_count}", 
                                             delta=f"{emergency_count/total_events:.1%} of total", 
                                             delta_color="inverse")
                        
                        with stat_col2:
                            # Miss distance statistics if available
                            miss_dist_field = None
                            for field in ['MISS_DISTANCE', 'MINIMUM_RANGE', 'MIN_RNG', 'RANGE']:
                                if field in data.columns:
                                    miss_dist_field = field
                                    break
                                    
                            if miss_dist_field:
                                # Convert to numeric
                                data[miss_dist_field] = pd.to_numeric(data[miss_dist_field], errors='coerce')
                                
                                # Calculate statistics
                                min_dist = data[miss_dist_field].min()
                                median_dist = data[miss_dist_field].median()
                                
                                st.metric("Closest Approach", f"{min_dist:.2f} km")
                                st.metric("Median Miss Distance", f"{median_dist:.2f} km")
                            
                            # Collision probability stats if available
                            if 'PC' in data.columns:
                                # Convert to numeric
                                data['PC'] = pd.to_numeric(data['PC'], errors='coerce')
                                
                                # Get max probability
                                max_prob = data['PC'].max()
                                high_risk = data[data['PC'] > 0.0001].shape[0]  # Commonly used threshold
                                
                                if not pd.isna(max_prob):
                                    st.metric("Highest Collision Probability", f"{max_prob:.6f}")
                                    if high_risk > 0:
                                        st.metric("High Risk Events (PC > 0.0001)", f"{high_risk}", 
                                                 delta=f"{high_risk/total_events:.1%} of total", 
                                                 delta_color="inverse")
                    
                    except Exception as stats_error:
                        st.warning(f"Could not calculate all conjunction statistics: {stats_error}")
                    
                    # Add interesting observations
                    st.subheader("Key Observations")
                    
                    # Create observations based on the data
                    observations = []
                    
                    try:
                        # Objects involved in conjunctions
                        object_cols = []
                        for col in ['OBJECT_NAME', 'SAT_1_NAME', 'OBJECT', 'PRIMARY_OBJECT']:
                            if col in data.columns:
                                object_cols.append(col)
                                
                        if object_cols:
                            main_obj_col = object_cols[0]
                            # Count unique objects
                            unique_objects = data[main_obj_col].nunique()
                            most_common = data[main_obj_col].value_counts().head(1)
                            if not most_common.empty:
                                most_common_name = most_common.index[0]
                                most_common_count = most_common.values[0]
                                observations.append(f"**{unique_objects}** unique objects were involved in conjunction events.")
                                observations.append(f"**{most_common_name}** was involved in the most conjunction events (**{most_common_count}** events).")
                        
                        # Time patterns
                        if 'CDM_TCA' in data.columns and not data['CDM_TCA'].isna().all():
                            # Convert to datetime
                            data['CDM_TCA'] = pd.to_datetime(data['CDM_TCA'], errors='coerce')
                            
                            # Group by day and count
                            daily_counts = data['CDM_TCA'].dt.date.value_counts()
                            if not daily_counts.empty:
                                max_day = daily_counts.idxmax()
                                max_day_count = daily_counts.max()
                                if max_day_count > 1:
                                    observations.append(f"**{max_day}** had the highest number of conjunction events (**{max_day_count}** events).")
                        
                        # Distance patterns
                        if miss_dist_field:
                            # Count close approaches (under 1 km)
                            close_approaches = data[data[miss_dist_field] < 1].shape[0]
                            if close_approaches > 0:
                                observations.append(f"**{close_approaches}** conjunction events had a miss distance less than **1 km**.")
                                
                            # Count very close approaches (under 100 meters)
                            very_close = data[data[miss_dist_field] < 0.1].shape[0]
                            if very_close > 0:
                                observations.append(f"**{very_close}** conjunction events had a miss distance less than **100 meters**.")
                    
                    except Exception as obs_error:
                        observations.append(f"_Note: Some observations could not be calculated due to data structure variations._")
                    
                    # Display observations
                    if observations:
                        for obs in observations:
                            st.markdown(obs)
                    else:
                        st.info("No specific patterns or observations could be extracted from this conjunction data set.")
                    
                    # Visualizations for conjunction data
                    st.subheader("Conjunction Analysis Visualizations")
                    
                    # Miss distance histogram if available
                    if 'MISS_DISTANCE' in data.columns:
                        try:
                            data['MISS_DISTANCE'] = pd.to_numeric(data['MISS_DISTANCE'], errors='coerce')
                            if not data['MISS_DISTANCE'].isna().all():
                                fig = px.histogram(
                                    data,
                                    x='MISS_DISTANCE',
                                    title='Distribution of Miss Distances',
                                    labels={'MISS_DISTANCE': 'Miss Distance (km)'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("No valid miss distance data found for visualization.")
                        except Exception as viz_error:
                            st.warning(f"Could not process miss distance data for visualization: {viz_error}")
                    else:
                        st.info("Miss distance data not available in the API response. This may be due to API changes.")
                    
                    # Time-based analysis if we have date information
                    if 'CDM_TCA' in data.columns and not data['CDM_TCA'].isna().all():
                        try:
                            st.subheader("Conjunction Events Timeline")
                            # Check for key fields that may have different names in different API versions
                            miss_dist_field = None
                            for field in ['MISS_DISTANCE', 'MINIMUM_RANGE', 'RANGE']:
                                if field in data.columns:
                                    miss_dist_field = field
                                    break
                                    
                            if miss_dist_field:
                                # Convert to numeric for plotting
                                data[miss_dist_field] = pd.to_numeric(data[miss_dist_field], errors='coerce')
                                
                                # Prepare hover data with whatever fields are available
                                hover_fields = []
                                for field in ['OBJECT', 'OBJECT_NAME', 'OBJECT_DESIGNATOR', 
                                           'OBJECT_2_NAME', 'OBJECT_2_DESIGNATOR', 'RELATIVE_SPEED']:
                                    if field in data.columns:
                                        hover_fields.append(field)
                                
                                # Plot timeline
                                fig = px.scatter(
                                    data, 
                                    x='CDM_TCA', 
                                    y=miss_dist_field,
                                    hover_data=hover_fields,
                                    title='Conjunction Events Over Time'
                                )
                                fig.update_layout(yaxis_title=f"{miss_dist_field} (km)", xaxis_title="Time of Closest Approach")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Could not find miss distance field in the data for timeline visualization.")
                        except Exception as timeline_error:
                            st.warning(f"Could not create timeline visualization: {timeline_error}")
                            
                    # Add more interesting visualizations if enough data is available
                    if len(data) >= 5:  # Only create this for datasets with enough points
                        try:
                            st.subheader("Conjunction Patterns Analysis")
                            
                            # Find appropriate columns for time, distance, and relative speed
                            time_col = None
                            dist_col = None
                            speed_col = None
                            
                            # Check for time column
                            for col in ['CDM_TCA', 'TCA', 'CLOSEST_APPROACH_TIME']:
                                if col in data.columns:
                                    time_col = col
                                    break
                                    
                            # Check for distance column
                            for col in ['MISS_DISTANCE', 'MIN_RNG', 'MINIMUM_RANGE', 'RANGE']:
                                if col in data.columns:
                                    dist_col = col
                                    break
                                    
                            # Check for relative speed column
                            for col in ['RELATIVE_SPEED', 'REL_SPEED', 'RELATIVE_VELOCITY']:
                                if col in data.columns:
                                    speed_col = col
                                    break
                            
                            # Additional columns for bubble chart and interactivity
                            object_col = None
                            for col in ['OBJECT_NAME', 'SAT_1_NAME', 'OBJECT', 'PRIMARY_OBJECT']:
                                if col in data.columns:
                                    object_col = col
                                    break
                                    
                            # Create a bubble chart if we have appropriate columns
                            if dist_col and speed_col:
                                # Convert columns to numeric
                                data[dist_col] = pd.to_numeric(data[dist_col], errors='coerce')
                                data[speed_col] = pd.to_numeric(data[speed_col], errors='coerce')
                                
                                # Create additional columns for better chart readability
                                data['risk_level'] = pd.cut(
                                    data[dist_col], 
                                    bins=[0, 0.1, 1, 10, float('inf')],
                                    labels=['Critical (< 100m)', 'High (100m-1km)', 'Moderate (1-10km)', 'Low (>10km)']
                                )
                                
                                # Define color map
                                risk_colors = {
                                    'Critical (< 100m)': 'red',
                                    'High (100m-1km)': 'orange',
                                    'Moderate (1-10km)': 'yellow',
                                    'Low (>10km)': 'green'
                                }
                                
                                # Create the bubble chart
                                fig = px.scatter(
                                    data,
                                    x=dist_col,
                                    y=speed_col,
                                    color='risk_level',
                                    size=[10] * len(data),  # Constant size for better visibility
                                    hover_name=object_col if object_col else None,
                                    title='Conjunction Risk Analysis: Miss Distance vs. Relative Speed',
                                    labels={
                                        dist_col: 'Miss Distance (km)',
                                        speed_col: 'Relative Speed (km/s)'
                                    },
                                    color_discrete_map=risk_colors
                                )
                                
                                # Add annotation lines for risk zones
                                fig.add_vline(x=0.1, line_width=1, line_dash="dash", line_color="red")
                                fig.add_vline(x=1, line_width=1, line_dash="dash", line_color="orange")
                                fig.add_vline(x=10, line_width=1, line_dash="dash", line_color="yellow")
                                
                                # Add explanation annotation
                                fig.add_annotation(
                                    text="Lower miss distance and higher relative speed = Higher risk",
                                    x=0.5, y=0.95,
                                    xref="paper", yref="paper",
                                    showarrow=False,
                                    font=dict(size=12)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Add explanatory text about the visualization
                                st.markdown("""
                                **Understanding the Risk Analysis Chart:**
                                - **Critical Risk Zone (Red)**: Miss distances under 100 meters represent critical collision risks
                                - **High Risk Zone (Orange)**: Miss distances between 100 meters and 1 km indicate high risk
                                - **Moderate Risk Zone (Yellow)**: Miss distances between 1-10 km require monitoring
                                - **Low Risk Zone (Green)**: Miss distances above 10 km generally pose little risk
                                
                                Higher relative speeds increase the severity of potential collisions, as they result in more debris generation.
                                """)
                            
                            else:
                                st.info("Missing required columns for advanced risk visualization. This may be due to Space-Track API changes.")
                                
                        except Exception as adv_viz_error:
                            st.warning(f"Could not create advanced conjunction pattern visualization: {adv_viz_error}")
                    
                except Exception as analysis_error:
                    st.error(f"Error during conjunction data analysis: {analysis_error}")
                    st.info("The data structure from Space-Track may have changed. You can still view and download the raw data above.")
                
                # Allow CSV download - should always work
                try:
                    csv = utils.convert_df_to_csv(data)
                    st.download_button(
                        label="Download conjunction data as CSV",
                        data=csv,
                        file_name="conjunction_data.csv",
                        mime="text/csv",
                    )
                except Exception as csv_error:
                    st.error(f"Error creating CSV download: {csv_error}")
            
            else:
                st.info("Click 'Load Conjunction Data' to view close approach information")
                
        elif data_category == "Boxscore Data":
            if st.sidebar.button("Load Boxscore Data"):
                with satellite_spinner("Loading boxscore data..."):
                    try:
                        data = db.get_space_track_data(engine, "boxscore")
                        if not data.empty:
                            st.session_state['boxscore_data'] = data
                        else:
                            st.warning("No boxscore data found. This could be due to Space-Track API changes or access restrictions.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                            else:
                                st.info("Try refreshing or selecting a different data category.")
                    except Exception as e:
                        st.error(f"Error retrieving boxscore data: {str(e)}")
                        st.info("Please try a different data category or contact Space-Track.org support if the issue persists.")
            
            if 'boxscore_data' in st.session_state:
                st.subheader("Space Objects Statistics by Country")
                
                # Display the data
                data = st.session_state['boxscore_data']
                
                # Check if we have any data
                if data.empty:
                    st.warning("The boxscore data returned is empty. Try a different data category.")
                else:
                    # Display raw data first to ensure something is visible
                    st.dataframe(data, use_container_width=True)
                    
                    # Add field explanations in an expandable section
                    with st.expander("Boxscore Data Fields Explanation"):
                        st.markdown("""
                        | Field | Description |
                        | --- | --- |
                        | COUNTRY | Country or organization responsible for the space objects |
                        | SPADOC_CD | Space Defense Operations Center code for the country |
                        | ORBITAL_PAYLOAD_COUNT | Number of operational satellites in orbit |
                        | ORBITAL_ROCKET_BODY_COUNT | Number of spent rocket bodies in orbit |
                        | ORBITAL_DEBRIS_COUNT | Number of cataloged debris objects in orbit |
                        | ORBITAL_TOTAL_COUNT | Total number of tracked objects in orbit for this country |
                        | DECAYED_PAYLOAD_COUNT | Number of satellites that have re-entered the atmosphere |
                        | DECAYED_ROCKET_BODY_COUNT | Number of rocket bodies that have re-entered |
                        | DECAYED_DEBRIS_COUNT | Number of debris pieces that have re-entered |
                        | DECAYED_TOTAL_COUNT | Total number of objects that have re-entered |
                        | TOTAL_PAYLOAD_COUNT | Total satellites (operational + re-entered) |
                        | TOTAL_ROCKET_BODY_COUNT | Total rocket bodies (in orbit + re-entered) |
                        | TOTAL_DEBRIS_COUNT | Total debris objects (in orbit + re-entered) |
                        | TOTAL_COUNT | Total objects associated with this country |
                        """)
                
                try:
                    # Check required columns exist
                    country_col = None
                    for col in ['COUNTRY', 'COUNTRY_OWNER', 'NATION']:
                        if col in data.columns:
                            country_col = col
                            break
                    
                    # Check if we have country information
                    if not country_col:
                        st.warning("Could not find country information in the data for visualization.")
                    else:
                        # Create visualizations
                        st.subheader("Comparative Analysis")
                        
                        # Convert any count columns to numeric
                        count_columns = []
                        for col in data.columns:
                            if any(term in col.upper() for term in ['COUNT', 'TOTAL', 'NUM']):
                                try:
                                    data[col] = pd.to_numeric(data[col], errors='coerce')
                                    count_columns.append(col)
                                except:
                                    pass
                        
                        # Find suitable total count column
                        total_count_col = None
                        for col in ['TOTAL_COUNT', 'TOTAL', 'PAYLOAD_COUNT']:
                            if col in data.columns:
                                total_count_col = col
                                break
                        
                        if total_count_col:
                            # Extract top countries by total objects
                            top_n = st.slider("Number of countries to show", 3, 20, 10)
                            top_countries = data.nlargest(top_n, total_count_col)
                            
                            # Find columns suitable for stacked/grouped visualization
                            plot_columns = [col for col in count_columns if col != total_count_col]
                            
                            if plot_columns and len(plot_columns) > 0:
                                # Create plot columns list with country column first
                                all_plot_cols = [country_col] + plot_columns
                                
                                # Check if we have enough data for a meaningful plot
                                if len(top_countries) > 0 and all(col in top_countries.columns for col in all_plot_cols):
                                    try:
                                        # Melt the data for grouped bar chart
                                        melted = top_countries[all_plot_cols].melt(
                                            id_vars=[country_col],
                                            var_name='Object Type',
                                            value_name='Count'
                                        )
                                        
                                        # Create a grouped bar chart
                                        fig = px.bar(
                                            melted,
                                            x=country_col,
                                            y='Count',
                                            color='Object Type',
                                            title=f'Top {top_n} Countries by Space Object Count',
                                            labels={country_col: 'Country', 'Count': 'Number of Objects'},
                                            barmode='group'
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                                    except Exception as plot_error:
                                        st.warning(f"Error creating grouped bar chart: {plot_error}")
                            
                            # Always try to create a simple visualization of total counts
                            try:
                                # Create a simple bar chart of top countries by total count
                                simple_fig = px.bar(
                                    top_countries,
                                    x=country_col,
                                    y=total_count_col,
                                    title=f'Top {top_n} Countries by Total Space Objects',
                                    color=total_count_col,
                                    color_continuous_scale='viridis'
                                )
                                st.plotly_chart(simple_fig, use_container_width=True)
                            except Exception as simple_plot_error:
                                st.warning(f"Error creating simple bar chart: {simple_plot_error}")
                        else:  # No total_count_col found
                            # If we don't have a good total count column but we have the country column
                            # Create a simple count by country
                            try:
                                country_counts = data[country_col].value_counts().reset_index()
                                country_counts.columns = ['Country', 'Count']
                                country_counts = country_counts.head(10)
                                
                                fig = px.bar(
                                    country_counts,
                                    x='Country',
                                    y='Count',
                                    title='Top 10 Countries by Object Count',
                                    color='Count',
                                    color_continuous_scale='viridis'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as fallback_error:
                                st.warning(f"Could not create fallback visualization: {fallback_error}")
                                st.info("The data structure may not be suitable for visualization.")
                
                except Exception as viz_error:
                    st.error(f"Error during boxscore data visualization: {viz_error}")
                    st.info("The data structure from Space-Track may have changed. You can still view and download the raw data above.")
                
                # Allow CSV download
                try:
                    csv = utils.convert_df_to_csv(data)
                    st.download_button(
                        label="Download boxscore data as CSV",
                        data=csv,
                        file_name="space_objects_by_country.csv",
                        mime="text/csv",
                    )
                except Exception as csv_error:
                    st.error(f"Error creating CSV download: {csv_error}")
                    
            
            
            else:
                st.info("Click 'Load Boxscore Data' to view statistics by country")
