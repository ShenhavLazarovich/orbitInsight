import streamlit as st
<<<<<<< Updated upstream
import auth
=======
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px
import space_track as st_api
import analysis as an
import visualization as vis
import utils
import enhanced_visualization as ev
import reports
import custom_layouts
import offline_manager
import point_settings
>>>>>>> Stashed changes

# Set page configuration
st.set_page_config(
    page_title="OrbitInsight",
    page_icon="🛰️",
    layout="wide",
)

<<<<<<< Updated upstream
# Initialize authentication
auth.init_db()

# Show login page if not authenticated
if not st.session_state.get('authenticated'):
    auth.login_page()
else:
    st.title("OrbitInsight Dashboard")
    st.write(f"Welcome, {st.session_state['username']}!")
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.rerun()

=======
# Add our custom CSS files
def add_custom_css():
    # Include our external CSS file
    with open('static/custom.css', 'r', encoding='utf-8') as css_file:
        css_content = css_file.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    
    # Add custom styling
    st.markdown("""
    <style>
        .welcome-card {
            background-color: rgba(16, 24, 39, 0.7);
        padding: 20px;
        border-radius: 10px;
            margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
        .welcome-card ul li {
            margin: 10px 0;
            color: #E0E0E0;
        }
        .welcome-card p {
            color: #E0E0E0;
        }
        .bmc-button {
            padding: 10px 20px;
            border-radius: 8px;
            background-color: #FFDD00;
            color: #000000 !important;
            text-decoration: none;
        font-weight: bold;
            display: inline-block;
            margin: 10px 0;
        border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .bmc-button:hover {
            background-color: #FFE838;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .category-option {
            background-color: rgba(26, 35, 50, 0.7);
            padding: 8px 15px;
            border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
            color: #E0E0E0;
            cursor: pointer;
            transition: all 0.3s ease;
    }
        .category-option.selected {
            border-color: #4F8BF9;
        background-color: rgba(79, 139, 249, 0.1);
        }
        .category-option:hover {
            border-color: #4F8BF9;
        }
        .capability-card {
            background-color: rgba(26, 35, 50, 0.7);
            padding: 20px;
        border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            transition: all 0.3s ease;
        }
        .capability-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-color: #4F8BF9;
        }
        .capability-card h4 {
            margin: 10px 0;
        }
        .capability-card p {
            color: #E0E0E0;
            font-size: 0.9em;
            margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Space-Track client
@st.cache_resource(show_spinner=False)
def get_space_track_client():
    """Get or create a Space-Track client with proper authentication"""
    # Check if credentials are in session state
    if not st.session_state.get("space_track_authenticated", False):
        return None
        
    try:
        client = st_api.SpaceTrackClient(
            username=st.session_state.get("username"),
            password=st.session_state.get("password")
        )
        return client  # Return the client without immediate authentication
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        st.session_state.space_track_authenticated = False
        return None

# Get satellite data from Space-Track
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_satellites(search_query=None):
    """Get satellite data with proper error handling and authentication checks"""
    if not st.session_state.get("space_track_authenticated", False):
        st.sidebar.warning("Please log in to search satellites.")
        return {}
    
    client = get_space_track_client()
    if not client:
        return {}
        
    # Try to authenticate the client
    try:
        if not client.authenticate():
            st.session_state.space_track_authenticated = False
            st.sidebar.error("Authentication failed. Please log in again.")
            return {}
    except Exception as e:
        st.session_state.space_track_authenticated = False
        st.sidebar.error(f"Authentication error: {str(e)}")
        return {}
        
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
            # Search by ID if the query is numeric
            if search_query.isdigit():
                results = client.get_latest_tle(norad_cat_id=search_query)
            else:
                results = client.get_latest_tle(satellite_name=search_query)
            
            if not results.empty:
                for _, sat in results.iterrows():
                    sat_id = str(sat['NORAD_CAT_ID'])
                    sat_name = str(sat['OBJECT_NAME'])
                    satellites_dict[sat_id] = sat_name
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                st.sidebar.error("Session expired. Please log in again.")
                st.session_state.space_track_authenticated = False
            else:
                st.sidebar.error(f"Error searching satellites: {str(e)}")
    
    return satellites_dict

def format_satellite_option(sat_id, sat_name):
    """Format satellite option for display in selectbox"""
    return f"{sat_name} (ID: {sat_id})"

def parse_satellite_option(option):
    """Parse satellite ID from the formatted option string"""
    if not option:
        return None
    # Extract ID from the format "Name (ID: 12345)"
    import re
    match = re.search(r'\(ID: (\d+)\)$', option)
    return match.group(1) if match else None

# Get trajectory data from Space-Track
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_trajectory_data(satellite_id, start_date, end_date):
    """Get and calculate satellite trajectory data"""
    client = get_space_track_client()
    if not client:
        return pd.DataFrame()
    
    try:
        # Get latest TLE data
        tle_data = client.get_latest_tle(norad_cat_id=satellite_id, limit=1)
        if tle_data.empty:
            st.error(f"No TLE data found for satellite ID {satellite_id}")
            return pd.DataFrame()
        
        # Calculate positions
        positions = calculate_positions(tle_data)
        return positions
    except Exception as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            st.error("Session expired. Please log in again.")
            st.session_state.space_track_authenticated = False
        else:
            st.error(f"Error getting trajectory data: {str(e)}")
        return pd.DataFrame()

def login_form():
    """Display and handle the Space-Track.org login form"""
    st.sidebar.title("Space-Track.org Login")
    
    # Initialize session state for login status if not exists
    if "space_track_authenticated" not in st.session_state:
        st.session_state.space_track_authenticated = False
    
    # If already logged in, show logout button and status
    if st.session_state.space_track_authenticated:
        st.sidebar.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.space_track_authenticated = False
            st.session_state.username = None
            st.session_state.password = None
            # Clear the cache when logging out
            st.cache_resource.clear()
            st.cache_data.clear()
            st.experimental_rerun()
        return True
    
    # Show login form
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
                return False
                
            # Try to authenticate
            try:
                client = st_api.SpaceTrackClient(username=username, password=password)
                if client.authenticate():
                    st.session_state.space_track_authenticated = True
                    st.session_state.username = username
                    st.session_state.password = password
                    # Clear any existing cache
                    st.cache_resource.clear()
                    st.cache_data.clear()
                    st.success("Successfully logged in!")
                    st.experimental_rerun()
                    return True
                else:
                    st.error("Authentication failed. Please check your credentials.")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
    
    return False

def show_welcome_message():
    """Display the welcome message and app description"""
    st.title("OrbitInsight 🛰️")
    
    # Main description container
    with st.container():
        st.markdown("""
        <div class="welcome-card">
            <p>Welcome to OrbitInsight - your window to the world of satellites and space objects. This application provides real-time tracking 
            and analysis of satellites using data from Space-Track.org.</p>
            <h3>Key Features</h3>
            <ul>
                <li>🛰️ Real-time satellite tracking and visualization</li>
                <li>🔍 Advanced search and monitoring capabilities</li>
                <li>📊 Detailed orbital statistics and analysis</li>
                <li>🌍 Interactive 2D/3D trajectory visualization</li>
                <li>📡 Space-Track.org data integration</li>
                <li>📱 Mobile-friendly responsive design</li>
                <li>💾 Offline mode with data caching</li>
                <li>📈 Custom dashboard layouts</li>
            </ul>
            <h3>Getting Started</h3>
            <ol>
                <li>Log in with your Space-Track.org credentials in the sidebar</li>
                <li>Search for a satellite by name or NORAD ID</li>
                <li>Select visualization options and customize the display</li>
                <li>Save your preferred layout for quick access</li>
            </ol>
            <p>Need help? Check out our documentation or contact support.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Support section container
    with st.container():
        st.markdown("""
        <div class="welcome-card" style="text-align: center;">
            <h3>Support OrbitInsight</h3>
            <p>If you find this tool helpful, consider supporting the project:</p>
            <a href="https://buymeacoffee.com/orbitinsight" target="_blank" class="bmc-button">
                ☕ Buy me a coffee
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    # Quick access buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("📖 Documentation", key="doc_button")
    with col2:
        st.button("💡 Tutorial", key="tutorial_button")
    with col3:
        st.button("❓ Help", key="help_button")

def show_data_categories():
    """Display the data category selection section"""
    st.markdown("""
    <div class="welcome-card">
        <h3>Available Data Categories</h3>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <div class="category-option selected">
                <h4>📡 Trajectories</h4>
                <p>Real-time satellite position tracking</p>
            </div>
            <div class="category-option">
                <h4>📚 Satellite Catalog</h4>
                <p>Comprehensive satellite database</p>
            </div>
            <div class="category-option">
                <h4>🚀 Launch Sites</h4>
                <p>Global launch facility information</p>
            </div>
            <div class="category-option">
                <h4>🔥 Decay Data</h4>
                <p>Re-entry and decay predictions</p>
            </div>
            <div class="category-option">
                <h4>⚠️ Conjunction Data</h4>
                <p>Close approach analysis</p>
            </div>
            <div class="category-option">
                <h4>📊 Boxscore Data</h4>
                <p>Statistical summaries by country</p>
            </div>
        </div>
        <div class="info-box" style="margin-top: 20px; padding: 15px; background: rgba(79, 139, 249, 0.1); border-radius: 5px;">
            <p style="margin: 0;">
                <span style="color: #FFD700;">💡</span> 
                Select a satellite and time period from the sidebar, then click 'Load Data' to begin analysis.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_platform_capabilities():
    """Display the platform capabilities section"""
    st.markdown("""
    <div class="welcome-card">
        <h3>Platform Capabilities</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
            <div class="capability-card">
                <div style="font-size: 2em;">📡</div>
                <h4>Real-time Data Access</h4>
                <p>Direct connection to Space-Track.org API with real-time satellite data updates and offline caching.</p>
            </div>
            <div class="capability-card">
                <div style="font-size: 2em;">🌍</div>
                <h4>Advanced Visualization</h4>
                <p>Interactive 2D/3D visualizations with customizable point display and density controls.</p>
            </div>
            <div class="capability-card">
                <div style="font-size: 2em;">📊</div>
                <h4>Comprehensive Analysis</h4>
                <p>Detailed orbital analysis, conjunction prediction, and anomaly detection capabilities.</p>
            </div>
            <div class="capability-card">
                <div style="font-size: 2em;">⚡</div>
                <h4>Enhanced Performance</h4>
                <p>Optimized data processing with smart caching and background synchronization.</p>
            </div>
            <div class="capability-card">
                <div style="font-size: 2em;">📱</div>
                <h4>Responsive Design</h4>
                <p>Mobile-friendly interface with adaptive layouts and touch support.</p>
            </div>
            <div class="capability-card">
                <div style="font-size: 2em;">💾</div>
                <h4>Offline Support</h4>
                <p>Robust offline capabilities with automatic data synchronization.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def format_metric_value(value, unit=""):
    """Safely format metric values with proper type checking"""
    try:
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{float(value):.2f}{unit}"
        return f"{value}{unit}"
    except:
        return "N/A"

# Initialize session state for new features
if 'offline_manager' not in st.session_state:
    st.session_state.offline_manager = offline_manager.OfflineManager()
    
if 'point_settings' not in st.session_state:
    st.session_state.point_settings = point_settings.PointVisualizationSettings()

def sync_callback(operation: str, data: dict):
    """Callback for offline data synchronization"""
    try:
        if operation == "cache_satellite":
            client = get_space_track_client()
            if client:
                client.update_satellite_data(data["satellite_id"], data["data"])
        # Add more sync operations as needed
    except Exception as e:
        st.error(f"Sync error: {str(e)}")

# Start sync thread for offline manager
st.session_state.offline_manager.start_sync_thread(sync_callback)

# Main app layout
def main():
    # Add custom CSS
    add_custom_css()
    
    # Render layout manager in sidebar
    selected_layout = custom_layouts.render_layout_manager()
    custom_layouts.apply_layout(selected_layout)
    
    # Add offline mode indicator and controls
    with st.sidebar:
        st.markdown("### Connection Status")
        is_online = st.session_state.get("space_track_authenticated", False)
        status_color = "green" if is_online else "red"
        st.markdown(f"<span style='color: {status_color}'>●</span> {'Online' if is_online else 'Offline'}", unsafe_allow_html=True)
        
        if not is_online:
            st.info("Working in offline mode. Data from cache will be used.")
            cache_stats = st.session_state.offline_manager.get_cache_stats()
            st.markdown("#### Cache Statistics")
            st.write(f"- Satellites: {cache_stats['satellite_count']}")
            st.write(f"- Trajectories: {cache_stats['trajectory_count']}")
            st.write(f"- Pending syncs: {cache_stats['pending_syncs']}")
    
    # Login form in sidebar
    login_form()
    
    # Satellite selection at top level
    st.sidebar.header("Satellite Selection")
    search_query = st.sidebar.text_input("Search satellites by name or NORAD ID")
    satellites_dict = get_satellites(search_query)
    
    if satellites_dict:
        satellite_options = [
            format_satellite_option(sat_id, name)
            for sat_id, name in satellites_dict.items()
        ]
        selected = st.sidebar.selectbox(
            "Select a satellite",
            options=[""] + satellite_options,
            index=0
        )
        
        if selected:
            st.session_state.selected_satellite = selected
            st.session_state.selected_satellite_id = parse_satellite_option(selected)
            
            # Get TLE data once for all tabs
            client = get_space_track_client()
            if client and st.session_state.selected_satellite_id:
                st.session_state.tle_data = client.get_latest_tle(norad_cat_id=st.session_state.selected_satellite_id)
    
    # Show home screen if no satellite is selected
    if not st.session_state.get("selected_satellite"):
        show_welcome_message()
        show_data_categories()
        show_platform_capabilities()
        return
    
    # Create tabs for different functionalities
    tab_titles = [
        "Satellite Overview",
        "Visualization & Tracking",
        "Conjunction Analysis",
        "Reports & Downloads"
    ]
    
    tabs = st.tabs(tab_titles)
    
    # Satellite Overview Tab
    with tabs[0]:
        st.header("Satellite Overview")
        col1, col2 = st.columns([2, 1])
                
        with col1:
            if st.session_state.selected_satellite and st.session_state.tle_data is not None and not st.session_state.tle_data.empty:
                st.subheader("Orbital Parameters")
                # Display orbital parameters in a clean layout
                metrics = {
                    "Inclination": ("INCLINATION", "°"),
                    "Eccentricity": ("ECCENTRICITY", ""),
                    "Period": ("PERIOD", "min"),
                    "Apogee": ("APOGEE", "km"),
                    "Perigee": ("PERIGEE", "km"),
                    "Mean Motion": ("MEAN_MOTION", "rev/day")
                }
                
                for label, (param, unit) in metrics.items():
                    if param in st.session_state.tle_data.columns:
                        value = st.session_state.tle_data.iloc[0][param]
                        formatted_value = format_metric_value(value, unit)
                        st.metric(label, formatted_value)
                    else:
                        st.metric(label, "N/A")
                
                # Display epoch information
                if "EPOCH" in st.session_state.tle_data.columns:
                    st.subheader("Epoch Information")
                    try:
                        epoch = pd.to_datetime(st.session_state.tle_data.iloc[0]["EPOCH"])
                        st.info(f"Last Update: {epoch.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    except:
                        st.info("Last Update: Not available")
        
        with col2:
            # Display satellite status and quick metrics
            if st.session_state.selected_satellite:
                st.subheader("Satellite Status")
                st.success("Active")
                
                # Add quick metrics with safe formatting
                if st.session_state.tle_data is not None and not st.session_state.tle_data.empty:
                    try:
                        altitude = st.session_state.tle_data.iloc[0].get('MEAN_ALTITUDE', 'N/A')
                        st.metric("Altitude", format_metric_value(altitude, " km"))
                        
                        velocity = st.session_state.tle_data.iloc[0].get('MEAN_MOTION', 'N/A')
                        st.metric("Velocity", format_metric_value(velocity, " km/s"))
                        
                        progress = 67  # This is a placeholder value
                        st.metric("Ground Track Progress", format_metric_value(progress, "%"))
                    except:
                        st.metric("Altitude", "N/A")
                        st.metric("Velocity", "N/A")
                        st.metric("Ground Track Progress", "N/A")
    
    # Visualization & Tracking Tab
    with tabs[1]:
        st.header("Visualization & Tracking")
        if st.session_state.selected_satellite:
            # Get trajectory data (with offline support)
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now() + timedelta(days=1)
            
            trajectory_data = None
            if st.session_state.get("space_track_authenticated", False):
                try:
                    trajectory_data = get_trajectory_data(
                        st.session_state.selected_satellite_id, 
                        start_date, end_date
                    )
                    # Cache the data for offline use
                    st.session_state.offline_manager.cache_trajectory_data(
                        st.session_state.selected_satellite_id,
                        trajectory_data,
                        start_date,
                        end_date
                    )
                except Exception:
                    st.warning("Failed to fetch online data, trying cache...")
                    trajectory_data = None
            
            if trajectory_data is None or trajectory_data.empty:
                trajectory_data = st.session_state.offline_manager.get_cached_trajectory_data(
                    st.session_state.selected_satellite_id,
                    start_date,
                    end_date
                )
            
            if not trajectory_data.empty:
                # Create sub-tabs for different views
                view_tabs = st.tabs(["Ground Track", "3D View", "2D View", "Orbital Parameters"])
                
                # Get point visualization settings
                point_viz_settings = st.session_state.point_settings.render_settings_ui()
                
                # Ground Track View
                with view_tabs[0]:
                    fig = vis.plot_ground_track(trajectory_data)
                    fig = st.session_state.point_settings.apply_settings_to_figure(
                        fig, trajectory_data[['latitude', 'longitude']].values
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 3D View
                with view_tabs[1]:
                    fig = vis.plot_3d_trajectory(
                        fig, trajectory_data[['x', 'y', 'z']].values
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 2D View
                with view_tabs[2]:
                    fig = vis.plot_2d_trajectory(
                        fig, trajectory_data[['x', 'y']].values
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Orbital Parameters
                with view_tabs[3]:
                    st.plotly_chart(vis.plot_orbital_parameters(trajectory_data))
            else:
                st.warning("No trajectory data available for the selected satellite.")
        else:
            st.info("Please select a satellite to view visualizations.")
    
    # Conjunction Analysis Tab
    with tabs[2]:
        st.header("Conjunction Analysis")
        if st.session_state.selected_satellite:
            # Get conjunction data
            client = get_space_track_client()
            if client:
                conjunction_data = client.get_conjunction_data(st.session_state.selected_satellite_id)
                
                if conjunction_data['status'] == 'success':
                    # Display conjunction analysis results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Risk Assessment")
                        risk_color = {
                            'high': 'red',
                            'medium': 'yellow',
                            'low': 'green'
                        }.get(conjunction_data['risk_level'], 'gray')
                        
                        st.markdown(f"**Risk Level:** :{risk_color}[{conjunction_data['risk_level'].upper()}]")
                        
                        if conjunction_data['min_distance']:
                            st.metric("Minimum Distance", f"{conjunction_data['min_distance']:.2f} km")
                    
                    with col2:
                        st.subheader("Conjunction Statistics")
                        st.metric("Past Approaches", conjunction_data['past_approaches'])
                        st.metric("Future Approaches", conjunction_data['future_approaches'])
                        st.metric("Tracked Objects", conjunction_data['tracked_objects'])
                else:
                    st.error(f"Error retrieving conjunction data: {conjunction_data.get('error', 'Unknown error')}")
        else:
            st.info("Please select a satellite to view conjunction analysis.")
    
    # Reports & Downloads Tab
    with tabs[3]:
        st.header("Reports & Downloads")
        if st.session_state.selected_satellite:
            # Generate reports
            report_types = [
                "Orbital Parameters Report",
                "Conjunction Analysis Report",
                "Ground Track Report"
            ]
            
            report_type = st.selectbox("Select Report Type", report_types)
            
            if st.button("Generate Report"):
                with st.spinner("Generating report..."):
                    if report_type == "Orbital Parameters Report":
                        report_data = reports.generate_orbital_parameters_report(st.session_state.tle_data)
                    elif report_type == "Conjunction Analysis Report":
                        report_data = reports.generate_conjunction_report(conjunction_data)
                    else:
                        report_data = reports.generate_ground_track_report(trajectory_data)
                
                st.download_button(
                    "Download Report",
                    report_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_{st.session_state.selected_satellite_id}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Please select a satellite to generate reports.")
                
if __name__ == "__main__":
    main() 
>>>>>>> Stashed changes
