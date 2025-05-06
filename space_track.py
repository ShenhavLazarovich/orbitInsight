import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import warnings

# Suppress SGP4 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class SpaceTrackClient:
    """
    Client for accessing Space-Track.org API to fetch satellite (CSpOC) data.
    Requires Space-Track.org credentials to be set as environment variables:
    - SPACETRACK_USERNAME
    - SPACETRACK_PASSWORD
    """
    BASE_URL = "https://www.space-track.org"
    AUTH_URL = f"{BASE_URL}/ajaxauth/login"
    
    def __init__(self):
        self.username = os.getenv("SPACETRACK_USERNAME")
        self.password = os.getenv("SPACETRACK_PASSWORD")
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with Space-Track.org"""
        if not self.username or not self.password:
            raise ValueError("Space-Track.org credentials not found in environment variables")
        
        credentials = {
            'identity': self.username,
            'password': self.password
        }
        
        try:
            response = self.session.post(self.AUTH_URL, data=credentials)
            response.raise_for_status()
            self.authenticated = True
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_latest_tle(self, norad_cat_id=None, satellite_name=None, limit=10):
        """
        Get latest Two-Line Element sets for satellites
        
        Args:
            norad_cat_id: NORAD Catalog ID (Number)
            satellite_name: Name of satellite (can include wildcards)
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with TLE data
        """
        if not self.authenticated and not self.authenticate():
            raise ConnectionError("Failed to authenticate with Space-Track.org")
            
        # Build query
        query_params = []
        if norad_cat_id:
            query_params.append(f"NORAD_CAT_ID/{norad_cat_id}")
        elif satellite_name:
            query_params.append(f"OBJECT_NAME/{satellite_name}")
            
        # Default to most recent data if no parameters provided
        if not query_params:
            query_params.append("ORDINAL/1")
            
        query_url = f"{self.BASE_URL}/basicspacedata/query/class/tle_latest/format/json"
        if query_params:
            query_url += f"/{''.join(query_params)}/limit/{limit}"
            
        try:
            response = self.session.get(query_url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TLE data: {e}")
            return pd.DataFrame()
        
    def get_satellite_catalog(self, limit=100):
        """
        Get the satellite catalog information
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with satellite catalog data
        """
        if not self.authenticated and not self.authenticate():
            raise ConnectionError("Failed to authenticate with Space-Track.org")
            
        # Order by launch date descending (newest first)
        query_url = f"{self.BASE_URL}/basicspacedata/query/class/satcat/format/json/orderby/LAUNCH_DATE%20desc/limit/{limit}"
            
        try:
            response = self.session.get(query_url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching satellite catalog: {e}")
            return pd.DataFrame()
    
    def get_satellite_positions(self, tle_data, time_start, time_end, time_step_minutes=10):
        """
        Calculate satellite positions from TLE data at specified time intervals.
        This requires the SGP4 propagator to calculate positions from TLE data.
        
        Args:
            tle_data: DataFrame containing TLE data
            time_start: Start time for trajectory calculation
            time_end: End time for trajectory calculation
            time_step_minutes: Time step between trajectory points in minutes
            
        Returns:
            DataFrame with satellite position data
        """
        try:
            from sgp4.earth_gravity import wgs72
            from sgp4.io import twoline2rv
        except ImportError:
            print("SGP4 library not installed. Install with: pip install sgp4")
            return pd.DataFrame()
        
        if tle_data.empty:
            return pd.DataFrame()
            
        # Prepare time range
        if isinstance(time_start, str):
            time_start = pd.to_datetime(time_start)
        if isinstance(time_end, str):
            time_end = pd.to_datetime(time_end)
            
        time_range = pd.date_range(start=time_start, end=time_end, freq=f'{time_step_minutes}min')
        
        # List to store all trajectory points
        trajectory_data = []
        
        for _, sat_row in tle_data.iterrows():
            # Extract TLE lines
            try:
                satellite_id = sat_row['NORAD_CAT_ID']
                satellite_name = sat_row['OBJECT_NAME']
                line1 = sat_row['TLE_LINE1']
                line2 = sat_row['TLE_LINE2']
                
                # Create satellite object from TLE
                satellite = twoline2rv(line1, line2, wgs72)
                
                # Calculate position at each time step
                for timestamp in time_range:
                    # Convert to SGP4 format time (minutes since epoch)
                    year, month, day, hour, minute, second = timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second
                    
                    # Get position and velocity
                    position, velocity = satellite.propagate(
                        year, month, day, hour, minute, second
                    )
                    
                    if position[0] is not None and not any(pd.isna(position)):
                        # Extract components
                        x, y, z = position
                        vx, vy, vz = velocity
                        
                        # Calculate altitude (distance from Earth center - Earth radius)
                        # Earth radius is approximately 6371 km
                        altitude = (x**2 + y**2 + z**2)**0.5 - 6371
                        
                        # Add data point to results
                        trajectory_data.append({
                            'satellite_id': satellite_id,
                            'object_name': satellite_name,
                            'timestamp': timestamp,
                            'x': x * 1000,  # Convert from km to m
                            'y': y * 1000,
                            'z': z * 1000,
                            'velocity_x': vx * 1000,  # Convert from km/s to m/s
                            'velocity_y': vy * 1000,
                            'velocity_z': vz * 1000,
                            'altitude': altitude * 1000  # Convert from km to m
                        })
            except Exception as e:
                print(f"Error processing satellite {satellite_id}: {e}")
                continue
                
        # Convert to DataFrame
        trajectory_df = pd.DataFrame(trajectory_data)
        return trajectory_df
        
    def close(self):
        """Close the session"""
        self.session.close()
        self.authenticated = False

def get_satellite_data(satellite_ids=None, start_date=None, end_date=None, limit=10):
    """
    Fetch satellite data from Space-Track.org and return it in a format 
    compatible with the dashboard.
    
    Args:
        satellite_ids: List of NORAD IDs to fetch 
        start_date: Start date for trajectory calculation
        end_date: End date for trajectory calculation
        limit: Maximum number of satellites to fetch if satellite_ids not provided
        
    Returns:
        Tuple of (satellite_list, trajectory_df) containing available satellites and trajectory data
    """
    # Default dates if not provided
    if not start_date:
        start_date = datetime.now() - timedelta(days=1)
    if not end_date:
        end_date = datetime.now()
        
    # Initialize client
    client = SpaceTrackClient()
    
    try:
        # Get TLE data
        if satellite_ids:
            # Fetch specific satellites
            all_tle_data = pd.DataFrame()
            for sat_id in satellite_ids:
                tle_data = client.get_latest_tle(norad_cat_id=sat_id)
                all_tle_data = pd.concat([all_tle_data, tle_data])
        else:
            # Get catalog of satellites for selection
            satcat = client.get_satellite_catalog(limit=limit)
            if not satcat.empty:
                # Convert satellite catalog to dashboard-friendly format with launch dates
                satellites = []
                for _, sat in satcat.iterrows():
                    if 'NORAD_CAT_ID' in sat and 'OBJECT_NAME' in sat:
                        # Include launch date if available
                        launch_date = sat.get('LAUNCH_DATE', 'Unknown')
                        # Create display name with launch date if available
                        display_name = sat['OBJECT_NAME']
                        if launch_date and launch_date != 'Unknown':
                            try:
                                # Format nicely if it's a valid date
                                launch_date_obj = pd.to_datetime(launch_date)
                                display_name = f"{sat['OBJECT_NAME']} (Launched: {launch_date_obj.strftime('%Y-%m-%d')})"
                            except:
                                # Use as is if can't parse
                                display_name = f"{sat['OBJECT_NAME']} (Launched: {launch_date})"
                        
                        satellites.append({
                            'id': sat['NORAD_CAT_ID'],
                            'name': display_name,
                            'launch_date': launch_date
                        })
                return satellites, pd.DataFrame()
            
            # If satellite_ids not provided and no catalog, fetch some popular satellites
            popular_satellites = ['ISS (ZARYA)', 'STARLINK', 'HUBBLE']
            all_tle_data = pd.DataFrame()
            for sat_name in popular_satellites:
                tle_data = client.get_latest_tle(satellite_name=f"{sat_name}%", limit=5)
                all_tle_data = pd.concat([all_tle_data, tle_data])
        
        # Calculate positions for the given time range
        trajectory_df = client.get_satellite_positions(
            all_tle_data, 
            time_start=start_date, 
            time_end=end_date,
            time_step_minutes=10
        )
        
        # Clean up
        client.close()
        
        # Create list of available satellites for selection
        available_satellites = []
        for sat_id in trajectory_df['satellite_id'].unique():
            sat_name = trajectory_df[trajectory_df['satellite_id'] == sat_id]['object_name'].iloc[0]
            available_satellites.append({
                'id': sat_id,
                'name': sat_name
            })
            
        return available_satellites, trajectory_df
        
    except Exception as e:
        print(f"Error fetching satellite data: {e}")
        client.close()
        return [], pd.DataFrame()