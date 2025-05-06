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

# Connect to database
try:
    engine = db.get_database_connection()
    # Get available satellites with names
    satellites_dict = db.get_satellites(engine)
    
    if not satellites_dict:
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
                        data = db.get_space_track_data(engine, "conjunction", days_back=days_back, limit=limit)
                        if not data.empty:
                            st.session_state['conjunction_data'] = data
                        else:
                            st.warning("No conjunction data found. Make sure Space-Track.org credentials are valid.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                    except Exception as e:
                        st.error(f"Error retrieving conjunction data: {str(e)}")
            
            if 'conjunction_data' in st.session_state:
                st.subheader("Conjunction Data Messages (Close Approaches)")
                
                # Display the data
                data = st.session_state['conjunction_data']
                
                # Format the data for better display
                if 'CDM_TCA' in data.columns:
                    # Try to convert to datetime for better sorting
                    try:
                        data['CDM_TCA'] = pd.to_datetime(data['CDM_TCA'], errors='coerce')
                    except:
                        pass
                
                # Filter conjunction data by minimum probability if available
                if 'PC' in data.columns:  # Probability of Collision
                    try:
                        data['PC'] = pd.to_numeric(data['PC'], errors='coerce')
                        min_prob = st.slider(
                            "Minimum Collision Probability", 
                            min_value=0.0, 
                            max_value=float(data['PC'].max() if not data['PC'].isna().all() else 1.0),
                            value=0.0,
                            step=0.0001
                        )
                        data = data[data['PC'] >= min_prob]
                    except:
                        st.warning("Could not process collision probability data.")
                
                st.dataframe(data, use_container_width=True)
                
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
                    except:
                        st.warning("Could not process miss distance data for visualization.")
                
                # Allow CSV download
                csv = utils.convert_df_to_csv(data)
                st.download_button(
                    label="Download conjunction data as CSV",
                    data=csv,
                    file_name="conjunction_data.csv",
                    mime="text/csv",
                )
            
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
                            st.warning("No boxscore data found. Make sure Space-Track.org credentials are valid.")
                            if not has_space_track_credentials:
                                st.info("Space-Track.org credentials are required to access this data.")
                    except Exception as e:
                        st.error(f"Error retrieving boxscore data: {str(e)}")
            
            if 'boxscore_data' in st.session_state:
                st.subheader("Space Objects Statistics by Country")
                
                # Display the data
                data = st.session_state['boxscore_data']
                st.dataframe(data, use_container_width=True)
                
                # Create visualizations
                st.subheader("Comparative Analysis")
                
                # Objects by country
                if 'COUNTRY' in data.columns and 'SPADOC_CD' in data.columns:
                    try:
                        # Extract top countries by total objects
                        top_n = st.slider("Number of countries to show", 3, 20, 10)
                        
                        # Convert count columns to numeric
                        count_columns = ['PAYLOAD_COUNT', 'PAYLOAD_DETAIL_COUNT', 'ROCKET_BODY_COUNT', 'DEBRIS_COUNT', 'TOTAL_COUNT']
                        for col in count_columns:
                            if col in data.columns:
                                data[col] = pd.to_numeric(data[col], errors='coerce')
                        
                        if 'TOTAL_COUNT' in data.columns:
                            top_countries = data.nlargest(top_n, 'TOTAL_COUNT')
                            
                            # Melt the data for grouped bar chart
                            plot_columns = [col for col in ['COUNTRY', 'PAYLOAD_COUNT', 'ROCKET_BODY_COUNT', 'DEBRIS_COUNT'] if col in top_countries.columns]
                            
                            if len(plot_columns) > 1:
                                melted = top_countries[plot_columns].melt(
                                    id_vars=['COUNTRY'],
                                    var_name='Object Type',
                                    value_name='Count'
                                )
                                
                                # Create a grouped bar chart
                                fig = px.bar(
                                    melted,
                                    x='COUNTRY',
                                    y='Count',
                                    color='Object Type',
                                    title=f'Top {top_n} Countries by Space Object Count',
                                    labels={'COUNTRY': 'Country', 'Count': 'Number of Objects'},
                                    barmode='group'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Insufficient data for comparative visualization.")
                        else:
                            st.warning("Total count data not available for visualization.")
                    except Exception as e:
                        st.error(f"Error creating visualization: {str(e)}")
                
                # Allow CSV download
                csv = utils.convert_df_to_csv(data)
                st.download_button(
                    label="Download boxscore data as CSV",
                    data=csv,
                    file_name="space_objects_by_country.csv",
                    mime="text/csv",
                )
            
            else:
                st.info("Click 'Load Boxscore Data' to view statistics by country")
