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
                with st.spinner(f"Loading satellite catalog data..."):
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
                
                # Display filtered data
                if selected_columns:
                    st.dataframe(data[selected_columns], use_container_width=True)
                else:
                    st.dataframe(data, use_container_width=True)
                
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
                with st.spinner("Loading launch sites data..."):
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
                with st.spinner("Loading decay data..."):
                    try:
                        data = db.get_space_track_data(engine, "decay", days_back=days_back, limit=limit)
                        if not data.empty:
                            st.session_state['decay_data'] = data
                        else:
                            st.warning("No decay data found. Make sure Space-Track.org credentials are valid.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                    except Exception as e:
                        st.error(f"Error retrieving decay data: {str(e)}")
            
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
                with st.spinner("Loading conjunction data..."):
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
                    # Display raw data first to ensure something is visible even if processing fails
                    st.dataframe(data, use_container_width=True)
                
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
                    
                    # Visualizations for conjunction data
                    st.subheader("Conjunction Analysis")
                    
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
                with st.spinner("Loading boxscore data..."):
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
