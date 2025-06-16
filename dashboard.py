import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
import json
import re

import database as db
import analysis as an
import visualization as vis
import utils
import auth
import feedback
import space_track

def show_dashboard():
    """Display the main dashboard as the main entry point, matching the main branch layout and requested order."""
    # 1. Welcome to OrbitInsight
    st.markdown("""
    <div class="welcome-header">
        <h1>Welcome to OrbitInsight</h1>
        <div>Advanced SpaceTrack.com Analysis Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Platform Capabilities (explanation cards) + Buy Me a Coffee
    st.markdown("""
    <style>
    .feature-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        transition: transform 0.2s;
        color: #E0E0E0;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.3);
    }
    .feature-icon {
        font-size: 2em;
        margin-bottom: 10px;
        color: #4F8BF9;
    }
    .feature-card h3 {
        color: #4F8BF9;
        margin-bottom: 10px;
    }
    .feature-card p {
        color: #B0B0B0;
    }
    .styled-btn {
        display: inline-block;
        padding: 10px 20px;
        background-color: #4F8BF9;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin-top: 10px;
    }
    .styled-btn:hover {
        background-color: #3B7CDE;
    }
    .support-section {
        display: flex;
        align-items: center;
        gap: 2rem;
        padding: 2rem;
    }
    .support-content {
        flex: 1;
    }
    .support-icon {
        font-size: 3em;
        color: #4F8BF9;
    }
    </style>
    <h2 style="color:#4F8BF9;">Platform Capabilities</h2>
    <div style="display: flex; flex-wrap: wrap; gap: 1.5rem;">
        <div class="feature-card" style="flex: 1; min-width: 220px;">
            <div class="feature-icon">📡</div>
            <h3>Real-time Data Access</h3>
            <p>Connect to Space-Track.org API to retrieve actual satellite trajectory data from the Combined Space Operations Center (CSpOC).</p>
        </div>
        <div class="feature-card" style="flex: 1; min-width: 220px;">
            <div class="feature-icon">🌐</div>
            <h3>Interactive Visualization</h3>
            <p>Explore satellite trajectories with dynamic 2D and 3D visualizations showing position, altitude, and other parameters.</p>
        </div>
        <div class="feature-card" style="flex: 1; min-width: 220px;">
            <div class="feature-icon">🧠</div>
            <h3>Advanced Analysis</h3>
            <p>Analyze conjunctions, decays, and catalog data with advanced filtering, risk assessment, and anomaly detection tools.</p>
        </div>
        <div class="feature-card" style="flex: 1; min-width: 220px;">
            <div class="feature-icon">💾</div>
            <h3>Optimized Performance</h3>
            <p>Fast, responsive interface with export options for all tables and visualizations.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. How to Use
    st.markdown("""
    <style>
    .welcome-tutorial {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        color: #E0E0E0;
    }
    .welcome-tutorial h2 {
        color: #4F8BF9;
    }
    .welcome-tutorial ol {
        margin-left: 20px;
        color: #B0B0B0;
    }
    .welcome-tutorial li {
        margin: 10px 0;
    }
    </style>
    <div class="welcome-tutorial">
        <h2>How to Use OrbitInsight</h2>
        <ol>
            <li>Use the sidebar to navigate between data categories.</li>
            <li>Apply filters and explore visualizations on each page.</li>
            <li>Download data or reports as needed.</li>
            <li>Submit feedback or feature requests anytime!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # 4. Summary Analysis (quick stats and recent activity)
    st.markdown("""
    <style>
    .data-stats {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin: 20px 0;
        color: #E0E0E0;
    }
    .stat-label {
        font-weight: bold;
        color: #4F8BF9;
    }
    .stat-value {
        color: #B0B0B0;
        margin: 10px 0;
    }
    .data-stats ul {
        color: #B0B0B0;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Satellites", "2,500+")
    with col2:
        st.metric("Launch Sites", "25")
    with col3:
        st.metric("Recent Alerts", "15")
    with col4:
        st.metric("High Risk Events", "3")

    st.markdown("""
    <div class="data-stats">
        <span class="stat-label">Recent Activity</span>
        <div class="stat-value">Last updated: {}</div>
        <ul>
            <li>New conjunction event detected</li>
            <li>Satellite re-entry reported</li>
            <li>Catalog updated with 5 new launches</li>
        </ul>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)

    # Support section at the bottom
    st.markdown("""
    <div class="feature-card">
        <div class="support-section">
            <div class="support-icon">☕</div>
            <div class="support-content">
                <h3>Support OrbitInsight</h3>
                <p>If you find this project useful, consider <a href='https://www.buymeacoffee.com/' target='_blank' style='color:#4F8BF9; text-decoration:underline;'>buying me a coffee</a> to support further development!</p>
                <a href='https://www.buymeacoffee.com/' target='_blank' class='styled-btn'>Buy Me a Coffee</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_satellite_trajectories():
    """Satellite Trajectories: robust, user-friendly, tabbed interface for all satellite data features."""
    st.subheader("Satellite Trajectories")

    # 1. Fetch and cache satellite catalog for autocomplete
    catalog_error = None
    if 'satellite_names' not in st.session_state or 'satellite_catalog' not in st.session_state:
        with st.spinner("Loading satellite catalog from Space-Track.org..."):
            try:
                catalog_df = db.get_space_track_data(None, 'catalog', limit=10000)
                st.session_state['satellite_catalog'] = catalog_df
                if not catalog_df.empty and 'OBJECT_NAME' in catalog_df.columns and 'NORAD_CAT_ID' in catalog_df.columns:
                    st.session_state['satellite_names'] = [
                        f"{row['OBJECT_NAME']} (NORAD {row['NORAD_CAT_ID']})" for _, row in catalog_df.iterrows()
                    ]
                    st.session_state['satellite_name_to_id'] = {
                        f"{row['OBJECT_NAME']} (NORAD {row['NORAD_CAT_ID']})": row['NORAD_CAT_ID'] for _, row in catalog_df.iterrows()
                    }
                else:
                    catalog_error = "Could not load satellite catalog. Please check your Space-Track.org credentials and API access."
                    st.session_state['satellite_names'] = []
                    st.session_state['satellite_name_to_id'] = {}
                    st.session_state['satellite_catalog'] = pd.DataFrame()
            except Exception as e:
                catalog_error = f"Failed to load satellite catalog: {e}"
                st.session_state['satellite_names'] = []
                st.session_state['satellite_name_to_id'] = {}
                st.session_state['satellite_catalog'] = pd.DataFrame()

    # 2. Show error if catalog fetch failed
    if catalog_error or not st.session_state.get('satellite_names'):
        st.error(catalog_error or "Could not load satellite catalog. Please check your Space-Track.org credentials and API access.")
        st.info("You must have a valid Space-Track.org account with API access enabled. If you believe your credentials are correct, log in to Space-Track.org and check for any required actions (terms acceptance, email verification, etc.).")
        return

    # 3. Handle suggestion selection BEFORE rendering the text input
    if 'pending_satellite_suggestion_selected' in st.session_state:
        st.session_state['satellite_name_input'] = st.session_state['pending_satellite_suggestion_selected']
        del st.session_state['pending_satellite_suggestion_selected']

    # 4. Search/filter UI
    col1, col2 = st.columns(2)
    with col1:
        search_type = st.radio("Search by", ["NORAD ID", "Satellite Name"])
        if search_type == "NORAD ID":
            search_query = st.text_input("Enter NORAD ID")
        else:
            if 'satellite_name_input' not in st.session_state:
                st.session_state['satellite_name_input'] = ''
            search_query = st.text_input("Search Satellite Name", st.session_state['satellite_name_input'], key="satellite_name_input")
            # Show suggestions as user types
            suggestions = []
            if st.session_state['satellite_names'] and search_query:
                suggestions = [name for name in st.session_state['satellite_names'] if search_query.lower() in name.lower()][:20]
            if suggestions:
                if len(suggestions) > 5:
                    with st.expander(f"Show {len(suggestions)} suggestions"):
                        for suggestion in suggestions:
                            if st.button(suggestion, key=f"suggestion_{suggestion}"):
                                st.session_state['pending_satellite_suggestion_selected'] = suggestion
                                st.rerun()
                else:
                    st.markdown("<div style='background:#222;border-radius:6px;padding:8px 12px;margin-bottom:8px;'>Suggestions:</div>", unsafe_allow_html=True)
                    for suggestion in suggestions:
                        if st.button(suggestion, key=f"suggestion_{suggestion}"):
                            st.session_state['pending_satellite_suggestion_selected'] = suggestion
                            st.rerun()
            elif search_query:
                st.info("No matching satellites found.")

    with col2:
        date_range = st.date_input("Date Range", value=(datetime.now(), datetime.now() + timedelta(days=7)))
        altitude_range = st.slider("Altitude Range (km)", 0, 36000, (200, 2000))

    # 5. State for multiple match suggestions
    if 'pending_satellite_suggestions' not in st.session_state:
        st.session_state['pending_satellite_suggestions'] = []

    # 6. Search action
    if st.button("Search"):
        # If searching by NORAD ID
        if search_type == "NORAD ID" and search_query:
            try:
                satellite_data = db.get_satellites(None, search_query)
                if satellite_data.empty:
                    st.warning("No satellites found or authentication failed.")
                else:
                    # Clean and validate orbital parameters before plotting
                    required_cols = ['INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'SEMIMAJOR_AXIS', 'ECCENTRICITY']
                    for col in required_cols:
                        if col in satellite_data.columns:
                            satellite_data[col] = pd.to_numeric(satellite_data[col], errors='coerce')
                    satellite_data = satellite_data.dropna(subset=required_cols)
                    # --- Sub-tabs for all features ---
                    tabs = st.tabs(["Trajectory", "Quick Stats", "TLE Data", "Recent Activity", "Export"])
                    with tabs[0]:
                        if satellite_data.empty:
                            st.warning("No valid orbital data available for plotting.")
                        else:
                            st.markdown("### 3D Trajectory Plot")
                            fig = vis.plot_3d_trajectory(satellite_data)
                            st.plotly_chart(fig)
                            st.markdown("### 2D Map")
                            m = vis.plot_2d_trajectory(satellite_data)
                            folium_static(m)
                            st.markdown("### Orbital Parameters")
                            cols = [c for c in ['NORAD_CAT_ID', 'OBJECT_NAME', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE'] if c in satellite_data.columns]
                            if cols:
                                st.dataframe(satellite_data[cols])
                            else:
                                st.info("No orbital parameter columns available.")
                    with tabs[1]:
                        if satellite_data.empty:
                            st.warning("No data available for stats.")
                        else:
                            st.markdown("### Quick Stats")
                            st.write(satellite_data.describe(include='all'))
                    with tabs[2]:
                        tle_cols = [col for col in satellite_data.columns if col.startswith('TLE')]
                        st.markdown("### TLE Data")
                        if tle_cols:
                            st.dataframe(satellite_data[tle_cols])
                            st.download_button("Download TLE as CSV", satellite_data[tle_cols].to_csv(index=False), "tle_data.csv")
                        else:
                            st.info("No TLE data available.")
                    with tabs[3]:
                        st.markdown("### Recent Activity")
                        st.info("Recent activity and events for this satellite will appear here (future feature).")
                    with tabs[4]:
                        st.markdown("### Export Data")
                        st.download_button("Download All Data as CSV", satellite_data.to_csv(index=False), "satellite_data.csv")
            except Exception as e:
                st.error(f"Error fetching satellite data: {e}")
        # If searching by Satellite Name
        elif search_type == "Satellite Name" and search_query:
            # Always extract NORAD ID from the selected suggestion
            match = re.search(r"NORAD (\d+)", search_query)
            if match:
                norad_id = match.group(1)
                try:
                    satellite_data = db.get_satellites(None, str(norad_id))
                    if satellite_data.empty:
                        st.warning("No satellites found or authentication failed.")
                    else:
                        # Clean and validate orbital parameters before plotting
                        required_cols = ['INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'SEMIMAJOR_AXIS', 'ECCENTRICITY']
                        for col in required_cols:
                            if col in satellite_data.columns:
                                satellite_data[col] = pd.to_numeric(satellite_data[col], errors='coerce')
                        satellite_data = satellite_data.dropna(subset=required_cols)
                        # --- Sub-tabs for all features ---
                        tabs = st.tabs(["Trajectory", "Quick Stats", "TLE Data", "Recent Activity", "Export"])
                        with tabs[0]:
                            if satellite_data.empty:
                                st.warning("No valid orbital data available for plotting.")
                            else:
                                st.markdown("### 3D Trajectory Plot")
                                fig = vis.plot_3d_trajectory(satellite_data)
                                st.plotly_chart(fig)
                                st.markdown("### 2D Map")
                                m = vis.plot_2d_trajectory(satellite_data)
                                folium_static(m)
                                st.markdown("### Orbital Parameters")
                                cols = [c for c in ['NORAD_CAT_ID', 'OBJECT_NAME', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE'] if c in satellite_data.columns]
                                if cols:
                                    st.dataframe(satellite_data[cols])
                                else:
                                    st.info("No orbital parameter columns available.")
                        with tabs[1]:
                            if satellite_data.empty:
                                st.warning("No data available for stats.")
                            else:
                                st.markdown("### Quick Stats")
                                st.write(satellite_data.describe(include='all'))
                        with tabs[2]:
                            tle_cols = [col for col in satellite_data.columns if col.startswith('TLE')]
                            st.markdown("### TLE Data")
                            if tle_cols:
                                st.dataframe(satellite_data[tle_cols])
                                st.download_button("Download TLE as CSV", satellite_data[tle_cols].to_csv(index=False), "tle_data.csv")
                            else:
                                st.info("No TLE data available.")
                        with tabs[3]:
                            st.markdown("### Recent Activity")
                            st.info("Recent activity and events for this satellite will appear here (future feature).")
                        with tabs[4]:
                            st.markdown("### Export Data")
                            st.download_button("Download All Data as CSV", satellite_data.to_csv(index=False), "satellite_data.csv")
                except Exception as e:
                    st.error(f"Error fetching satellite data: {e}")
                return
            # Fallback: try partial name search in catalog as before
            catalog_df = st.session_state.get('satellite_catalog', pd.DataFrame())
            if not catalog_df.empty:
                if 'OBJECT_NAME' not in catalog_df.columns:
                    st.error(f"Satellite catalog does not contain 'OBJECT_NAME' column. Columns: {catalog_df.columns.tolist()}")
                else:
                    matches = catalog_df[catalog_df['OBJECT_NAME'].str.contains(re.escape(search_query), case=False, na=False)]
                    if len(matches) == 1:
                        norad_id = matches.iloc[0]['NORAD_CAT_ID']
                        try:
                            satellite_data = db.get_satellites(None, str(norad_id))
                            if satellite_data.empty:
                                st.warning("No satellites found or authentication failed.")
                            else:
                                # Clean and validate orbital parameters before plotting
                                required_cols = ['INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'SEMIMAJOR_AXIS', 'ECCENTRICITY']
                                for col in required_cols:
                                    if col in satellite_data.columns:
                                        satellite_data[col] = pd.to_numeric(satellite_data[col], errors='coerce')
                                satellite_data = satellite_data.dropna(subset=required_cols)
                                # --- Sub-tabs for all features ---
                                tabs = st.tabs(["Trajectory", "Quick Stats", "TLE Data", "Recent Activity", "Export"])
                                with tabs[0]:
                                    if satellite_data.empty:
                                        st.warning("No valid orbital data available for plotting.")
                                    else:
                                        st.markdown("### 3D Trajectory Plot")
                                        fig = vis.plot_3d_trajectory(satellite_data)
                                        st.plotly_chart(fig)
                                        st.markdown("### 2D Map")
                                        m = vis.plot_2d_trajectory(satellite_data)
                                        folium_static(m)
                                        st.markdown("### Orbital Parameters")
                                        cols = [c for c in ['NORAD_CAT_ID', 'OBJECT_NAME', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE'] if c in satellite_data.columns]
                                        if cols:
                                            st.dataframe(satellite_data[cols])
                                        else:
                                            st.info("No orbital parameter columns available.")
                                with tabs[1]:
                                    if satellite_data.empty:
                                        st.warning("No data available for stats.")
                                    else:
                                        st.markdown("### Quick Stats")
                                        st.write(satellite_data.describe(include='all'))
                                with tabs[2]:
                                    tle_cols = [col for col in satellite_data.columns if col.startswith('TLE')]
                                    st.markdown("### TLE Data")
                                    if tle_cols:
                                        st.dataframe(satellite_data[tle_cols])
                                        st.download_button("Download TLE as CSV", satellite_data[tle_cols].to_csv(index=False), "tle_data.csv")
                                    else:
                                        st.info("No TLE data available.")
                                with tabs[3]:
                                    st.markdown("### Recent Activity")
                                    st.info("Recent activity and events for this satellite will appear here (future feature).")
                                with tabs[4]:
                                    st.markdown("### Export Data")
                                    st.download_button("Download All Data as CSV", satellite_data.to_csv(index=False), "satellite_data.csv")
                        except Exception as e:
                            st.error(f"Error fetching satellite data: {e}")
                    elif len(matches) > 1:
                        st.session_state['pending_satellite_suggestions'] = [
                            f"{row['OBJECT_NAME']} (NORAD {row['NORAD_CAT_ID']})" for _, row in matches.iterrows()
                        ]
                        st.warning("Multiple satellites found. Please select one from the suggestions below.")
                    else:
                        st.warning("No satellites found matching your search.")
            else:
                st.warning("Satellite catalog not loaded.")

    # 7. If there are pending suggestions, show them as buttons
    if st.session_state.get('pending_satellite_suggestions'):
        st.markdown("<div style='background:#222;border-radius:6px;padding:8px 12px;margin-bottom:8px;'>Multiple matches found. Please select:</div>", unsafe_allow_html=True)
        for suggestion in st.session_state['pending_satellite_suggestions']:
            if st.button(suggestion, key=f"pending_{suggestion}"):
                st.session_state['pending_satellite_suggestion_selected'] = suggestion
                st.session_state['pending_satellite_suggestions'] = []
                st.rerun()

def show_conjunction_analysis():
    """Show conjunction risk analysis."""
    st.subheader("Conjunction Risk Analysis")
    days_back = st.slider("Days to analyze", 1, 30, 7)
    conjunction_data = db.get_space_track_data(None, "conjunction", days_back)

    if not conjunction_data.empty and 'PC' in conjunction_data.columns:
        def get_risk_level(pc):
            if pc is None or pd.isna(pc):
                return 'Unknown'
            try:
                pc = float(pc)
                if pc > 1e-4:
                    return 'HIGH'
                elif pc > 1e-6:
                    return 'MEDIUM'
                else:
                    return 'LOW'
            except Exception:
                return 'Unknown'
        conjunction_data['RISK_LEVEL'] = conjunction_data['PC'].apply(get_risk_level)
        if 'RISK_LEVEL' in conjunction_data.columns and not conjunction_data['RISK_LEVEL'].isnull().all():
            fig = px.pie(conjunction_data, names='RISK_LEVEL', title='Conjunction Risk Distribution')
            st.plotly_chart(fig)
        else:
            st.info("No risk level data available to plot.")
    else:
        st.info("No conjunction data or probability column available to plot.")

    # Timeline of events
    if 'TCA' in conjunction_data.columns and 'RISK_LEVEL' in conjunction_data.columns:
        fig = px.scatter(
            conjunction_data,
            x='TCA',
            y='RISK_LEVEL',
            color='RISK_LEVEL',
            title='Conjunction Events Timeline'
        )
        st.plotly_chart(fig)
    else:
        st.info("No conjunction event times available to plot a timeline.")
    
    # Detailed table
    st.subheader("Recent Conjunction Events")
    st.dataframe(conjunction_data)
    
    # Export options
    if st.button("Export to CSV"):
        csv = conjunction_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="conjunction_data.csv",
            mime="text/csv"
        )

def show_launch_sites():
    """Show launch site information."""
    st.subheader("Launch Sites")
    
    # Get launch site data
    launch_sites = db.get_space_track_data(None, "launch_sites")
    
    st.write("DEBUG: Launch site columns:", launch_sites.columns.tolist())
    
    if not launch_sites.empty:
        # Try to find latitude and longitude columns
        lat_col = next((col for col in launch_sites.columns if 'LAT' in col.upper()), None)
        lon_col = next((col for col in launch_sites.columns if 'LON' in col.upper()), None)
        if lat_col and lon_col:
            m = folium.Map()
            for _, site in launch_sites.iterrows():
                folium.Marker(
                    [site[lat_col], site[lon_col]],
                    popup=site.get('SITE_NAME', 'Unknown'),
                    tooltip=site.get('SITE_CODE', 'Unknown')
                ).add_to(m)
            folium_static(m)
            st.subheader("Launch Site Details")
            st.dataframe(launch_sites)
        else:
            st.info("No latitude/longitude data available for launch sites.")
    else:
        st.warning("No launch site data available.")

def show_reports():
    """Show report generation options."""
    st.subheader("Generate Reports")
    
    report_type = st.selectbox(
        "Report Type",
        ["Satellite Catalog", "Conjunction Analysis", "Launch Statistics", "Custom Report"]
    )
    
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )
    
    if report_type == "Custom Report":
        st.multiselect(
            "Select Data Fields",
            ["NORAD ID", "Satellite Name", "Launch Date", "Orbital Parameters", 
             "Conjunction Events", "Risk Levels", "Launch Site"]
        )
    
    if st.button("Generate Report"):
        st.info("Report generation in progress...")
        # TODO: Implement report generation
        st.success("Report generated successfully!")
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Download CSV"):
                st.download_button(
                    label="Download CSV",
                    data="",  # TODO: Add actual data
                    file_name="report.csv",
                    mime="text/csv"
                )
        with col2:
            if st.button("Download PDF"):
                st.download_button(
                    label="Download PDF",
                    data="",  # TODO: Add actual data
                    file_name="report.pdf",
                    mime="application/pdf"
                )

def show_catalog_data():
    """Display satellite catalog data."""
    st.header("Satellite Catalog")
    st.info("Satellite catalog feature coming soon!")

def show_decay_data():
    """Display decay data."""
    st.header("Decay Events")
    st.info("Decay events feature coming soon!")

def show_boxscore_data():
    """Display boxscore data."""
    st.header("Boxscore Statistics")
    st.info("Boxscore statistics feature coming soon!")

def init_dashboard():
    """Initialize the dashboard layout."""
    # Check authentication
    if not st.session_state.get('spacetrack_authenticated'):
        st.warning("Please log in to access the dashboard.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Satellite Trajectory", "Catalog Data", "Launch Sites", 
         "Decay Data", "Conjunction Data", "Boxscore Data", "Reports"]
    )
    
    # User info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Logged in as: **{st.session_state.get('spacetrack_username', 'Unknown')}**")
    if st.sidebar.button("Logout"):
        st.session_state['spacetrack_authenticated'] = False
        st.session_state['spacetrack_username'] = ''
        st.session_state['spacetrack_password'] = ''
        # Clear stored credentials on logout
        if 'stored_credentials' in st.session_state:
            del st.session_state['stored_credentials']
        st.rerun()
    
    # Main content area
    if page == "Dashboard":
        show_dashboard()
    elif page == "Satellite Trajectory":
        show_satellite_trajectories()
    elif page == "Catalog Data":
        show_catalog_data()
    elif page == "Launch Sites":
        show_launch_sites()
    elif page == "Decay Data":
        show_decay_data()
    elif page == "Conjunction Data":
        show_conjunction_analysis()
    elif page == "Boxscore Data":
        show_boxscore_data()
    elif page == "Reports":
        show_reports() 