import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import warnings
import math

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
    
    def __init__(self, username=None, password=None):
        # Allow direct credential passing or fall back to environment variables
        self.username = username or os.getenv("SPACETRACK_USERNAME")
        self.password = password or os.getenv("SPACETRACK_PASSWORD")
        self.session = requests.Session()
        self.authenticated = False
        self.last_auth_time = None
    
    def authenticate(self):
        """Authenticate with Space-Track.org"""
        if not self.username or not self.password:
            raise ValueError("Space-Track.org credentials not found. Please provide username and password.")
        
        credentials = {
            'identity': self.username,
            'password': self.password
        }
        
        try:
            response = self.session.post(self.AUTH_URL, data=credentials)
            response.raise_for_status()
            self.authenticated = True
            self.last_auth_time = datetime.now()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            self.authenticated = False
            return False
    
    def _ensure_authenticated(self):
        """Ensure the client is authenticated before making requests"""
        # If not authenticated or session is older than 5 minutes, re-authenticate
        if not self.authenticated or (
            self.last_auth_time and 
            (datetime.now() - self.last_auth_time).total_seconds() > 300
        ):
            if not self.authenticate():
                raise Exception("Failed to authenticate with Space-Track.org")
    
    def _query(self, query_path):
        """
        Execute a query against the Space-Track API
        
        Args:
            query_path: The query path after the base URL
            
        Returns:
            JSON response data or None on error
        """
        self._ensure_authenticated()
        
        try:
            query_url = f"{self.BASE_URL}/basicspacedata{query_path}"
            response = self.session.get(query_url)
            
            # Check for authentication errors
            if response.status_code == 401:
                # Try to re-authenticate once
                self.authenticated = False
                self._ensure_authenticated()
                # Retry the request
                response = self.session.get(query_url)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error executing query: {e}")
            if "401" in str(e) or "Unauthorized" in str(e):
                self.authenticated = False
            return None
    
    def get_latest_tle(self, norad_cat_id=None, satellite_name=None, limit=10):
        """
        Get the latest TLE data for a satellite
        
        Args:
            norad_cat_id: NORAD Catalog ID of the satellite
            satellite_name: Name of the satellite
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with TLE data
        """
        try:
            self._ensure_authenticated()
            
            # Special handling for ISS
            if satellite_name and "ISS" in satellite_name.upper():
                try:
                    return self.get_latest_tle(norad_cat_id=25544)  # ISS NORAD ID
                except:
                    satellite_name = "ISS (ZARYA)"
            
            # Build query parameters
            query_parts = [
                'class/tle_latest',
                'format/json',
                'orderby/EPOCH desc',
                f'limit/{limit}'
            ]
            
            # Add search criteria
            if norad_cat_id:
                query_parts.append(f'NORAD_CAT_ID/{norad_cat_id}')
            elif satellite_name:
                clean_name = satellite_name.upper().strip()
                if "ISS (ZARYA)" in clean_name:
                    query_parts.append('OBJECT_NAME/ISS (ZARYA)')
                else:
                    query_parts.append(f'OBJECT_NAME/like/{clean_name}%')
            
            query = '/'.join(query_parts)
            query_url = f"{self.BASE_URL}/basicspacedata/query/{query}"
            
            print(f"Querying Space-Track API: {query_url}")
            response = self.session.get(query_url)
            
            if response.status_code == 401:
                self.authenticated = False
                self._ensure_authenticated()
                response = self.session.get(query_url)
            elif response.status_code == 500:
                print("Server error with primary endpoint, trying alternative...")
                alt_query_parts = [
                    'class/gp',
                    'format/json',
                    'orderby/EPOCH desc',
                    f'limit/{limit}'
                ]
                
                if norad_cat_id:
                    alt_query_parts.append(f'NORAD_CAT_ID/{norad_cat_id}')
                elif satellite_name:
                    if "ISS (ZARYA)" in clean_name:
                        alt_query_parts.append('OBJECT_NAME/ISS (ZARYA)')
                    else:
                        alt_query_parts.append(f'OBJECT_NAME/like/{clean_name}%')
                
                alt_query = '/'.join(alt_query_parts)
                alt_url = f"{self.BASE_URL}/basicspacedata/query/{alt_query}"
                print(f"Trying alternative URL: {alt_url}")
                response = self.session.get(alt_url)
            
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return pd.DataFrame()
            
            print("Available columns in TLE data:", df.columns.tolist())
            
            if 'TLE_LINE1' not in df.columns or 'TLE_LINE2' not in df.columns:
                if 'line1' in df.columns and 'line2' in df.columns:
                    df = df.rename(columns={'line1': 'TLE_LINE1', 'line2': 'TLE_LINE2'})
                elif 'LINE1' in df.columns and 'LINE2' in df.columns:
                    df = df.rename(columns={'LINE1': 'TLE_LINE1', 'LINE2': 'TLE_LINE2'})
                else:
                    required_fields = [
                        'OBJECT_NAME', 'NORAD_CAT_ID', 'CLASSIFICATION_TYPE',
                        'EPOCH', 'MEAN_MOTION', 'ECCENTRICITY', 'INCLINATION',
                        'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'MEAN_ANOMALY',
                        'EPHEMERIS_TYPE', 'ELEMENT_SET_NO'
                    ]
                    
                    if all(field in df.columns for field in required_fields):
                        print("Constructing TLE lines from orbital elements")
                        raise ValueError("TLE line construction from elements not yet implemented")
                    else:
                        print("Missing required fields for TLE construction")
                        print("Available fields:", df.columns.tolist())
                        raise ValueError("Could not find or construct TLE lines from available data")
            
            return df
        
        except requests.exceptions.RequestException as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                self.authenticated = False
                raise Exception("Session expired. Please authenticate again.")
            elif "500" in str(e):
                raise Exception("Space-Track.org server error. Please try again later or try searching by NORAD ID (25544 for ISS).")
            raise Exception(f"Error fetching TLE data: {str(e)}")
    
    def get_satellite_catalog(self, limit=200):
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
            
    def get_launch_sites(self, limit=100):
        """
        Get launch site information
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with launch site data
        """
        if not self.authenticated and not self.authenticate():
            raise ConnectionError("Failed to authenticate with Space-Track.org")
            
        query_url = f"{self.BASE_URL}/basicspacedata/query/class/launch_site/format/json/orderby/SITE_CODE/limit/{limit}"
            
        try:
            response = self.session.get(query_url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching launch site data: {e}")
            return pd.DataFrame()
    
    def get_decay_data(self, days_back=30, limit=100):
        """
        Get decay data for objects that have re-entered Earth's atmosphere
        
        Args:
            days_back: Number of days in the past to retrieve data for
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with decay data
        """
        if not self.authenticated and not self.authenticate():
            raise ConnectionError("Failed to authenticate with Space-Track.org")
        
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Try multiple possible column names and endpoints for decay data
        attempted_endpoints = []
        
        # Try all combinations of class and date column names for decay data
        decay_classes = ["decay", "decays", "satcat", "decay-data", "reentry"]
        date_columns = ["DECAY_DATE", "DECAY", "DECAY_EPOCH", "REENTRY_DATE", "REENTRY"]
        
        # Try each combination systematically with detailed error reporting
        for decay_class in decay_classes:
            for date_column in date_columns:
                try:
                    print(f"Trying decay endpoint with class={decay_class}, column={date_column}...")
                    query_url = f"{self.BASE_URL}/basicspacedata/query/class/{decay_class}/format/json/{date_column}/>{start_date}/{date_column}/<{end_date}/orderby/{date_column}%20desc/limit/{limit}"
                    attempted_endpoints.append(f"{decay_class} with {date_column}")
                    
                    print(f"Requesting URL: {query_url}")
                    response = self.session.get(query_url)
                    
                    # Print the full response for debugging
                    print(f"Response status: {response.status_code}")
                    if response.status_code != 200:
                        print(f"Response text: {response.text[:200]}...")
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if data:
                        df = pd.DataFrame(data)
                        if not df.empty:
                            return df
                except Exception as e:
                    print(f"Error with endpoint {decay_class}/{date_column}: {str(e)}")
                    continue
        
        print(f"No successful endpoints found. Attempted: {', '.join(attempted_endpoints)}")
        return pd.DataFrame()

    def get_conjunction_data(self, satellite_id, days_before=7, days_after=7):
        """
        Get conjunction data for a satellite
        
        Args:
            satellite_id: NORAD Catalog ID of the satellite
            days_before: Number of days before current date to check
            days_after: Number of days after current date to check
            
        Returns:
            Dictionary containing conjunction analysis results
        """
        try:
            if not self.authenticated and not self.authenticate():
                return {'status': 'error', 'error': 'Authentication failed'}
            
            # Calculate date range
            end_date = datetime.now() + timedelta(days=days_after)
            start_date = datetime.now() - timedelta(days=days_before)
            
            # Query conjunction data
            query_url = (
                f"{self.BASE_URL}/basicspacedata/query/class/cdm/format/json"
                f"/CREATION_DATE/>{start_date.strftime('%Y-%m-%d')}"
                f"/CREATION_DATE/<{end_date.strftime('%Y-%m-%d')}"
                f"/orderby/TCA%20asc"
            )
            
            response = self.session.get(query_url)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {
                    'status': 'success',
                    'risk_level': 'low',
                    'min_distance': None,
                    'past_approaches': 0,
                    'future_approaches': 0,
                    'tracked_objects': 0
                }
            
            # Process conjunction data
            df = pd.DataFrame(data)
            df['TCA'] = pd.to_datetime(df['TCA'])
            
            # Filter for the specified satellite
            df = df[
                (df['OBJECT1_NORAD_CAT_ID'] == str(satellite_id)) |
                (df['OBJECT2_NORAD_CAT_ID'] == str(satellite_id))
            ]
            
            if df.empty:
                return {
                    'status': 'success',
                    'risk_level': 'low',
                    'min_distance': None,
                    'past_approaches': 0,
                    'future_approaches': 0,
                    'tracked_objects': 0
                }
            
            # Calculate statistics
            now = pd.Timestamp.now()
            past_approaches = len(df[df['TCA'] < now])
            future_approaches = len(df[df['TCA'] >= now])
            
            # Calculate minimum distance
            min_distance = df['MIN_RANGE'].astype(float).min()
            
            # Determine risk level based on minimum distance
            risk_level = 'low'
            if min_distance < 1.0:  # Less than 1 km
                risk_level = 'high'
            elif min_distance < 5.0:  # Less than 5 km
                risk_level = 'medium'
            
            # Count unique tracked objects
            tracked_objects = len(
                set(df['OBJECT1_NORAD_CAT_ID'].unique()) |
                set(df['OBJECT2_NORAD_CAT_ID'].unique())
            )
            
            return {
                'status': 'success',
                'risk_level': risk_level,
                'min_distance': float(min_distance),
                'past_approaches': int(past_approaches),
                'future_approaches': int(future_approaches),
                'tracked_objects': int(tracked_objects)
            }
            
        except requests.exceptions.RequestException as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                self.authenticated = False
                return {'status': 'error', 'error': 'Session expired. Please authenticate again.'}
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            return {'status': 'error', 'error': f'Unexpected error: {str(e)}'}
            
    def get_boxscore_data(self, limit=100):
        """
        Get boxscore data (satellite statistics by country)
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Pandas DataFrame with boxscore data
        """
        try:
            if not self.authenticated and not self.authenticate():
                raise ConnectionError("Failed to authenticate with Space-Track.org")
            
            query_url = f"{self.BASE_URL}/basicspacedata/query/class/boxscore/format/json/orderby/COUNTRY%20asc/limit/{limit}"
            
            response = self.session.get(query_url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return pd.DataFrame()
            
            return df
            
        except requests.exceptions.RequestException as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                self.authenticated = False
                raise Exception("Session expired. Please authenticate again.")
            raise Exception(f"Error fetching boxscore data: {str(e)}")
    
    def get_satellite_positions(self, tle_data, start_date, end_date, time_step_minutes=5):
        """
        Calculate satellite positions for a given time period using TLE data
        
        Args:
            tle_data: DataFrame containing TLE data
            start_date: Start date for position calculation
            end_date: End date for position calculation
            time_step_minutes: Time step between position calculations in minutes
            
        Returns:
            DataFrame with satellite positions over time
        """
        try:
            if tle_data.empty:
                raise ValueError("No TLE data provided")
            
            if 'TLE_LINE1' not in tle_data.columns or 'TLE_LINE2' not in tle_data.columns:
                raise ValueError("TLE data missing required line1/line2 elements")
            
            # Convert dates to datetime if they're strings
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            
            # Create time points for position calculation
            time_points = pd.date_range(
                start=start_date,
                end=end_date,
                freq=f'{time_step_minutes}T'
            )
            
            # Get the latest TLE data
            latest_tle = tle_data.iloc[0]
            
            # Initialize lists for position data
            positions = []
            
            # Calculate positions at each time point
            for t in time_points:
                try:
                    # Calculate position
                    pos = self._calculate_position(
                        latest_tle['TLE_LINE1'],
                        latest_tle['TLE_LINE2'],
                        t
                    )
                    
                    if pos is not None:
                        positions.append({
                            'timestamp': t,
                            'x': pos[0],
                            'y': pos[1],
                            'z': pos[2],
                            'latitude': pos[3],
                            'longitude': pos[4],
                            'altitude': pos[5]
                        })
                except Exception as e:
                    print(f"Error calculating position at {t}: {str(e)}")
                    continue
            
            # Convert to DataFrame
            if positions:
                return pd.DataFrame(positions)
            else:
                return pd.DataFrame(columns=['timestamp', 'x', 'y', 'z', 'latitude', 'longitude', 'altitude'])
            
        except Exception as e:
            print(f"Error calculating satellite positions: {str(e)}")
            return pd.DataFrame(columns=['timestamp', 'x', 'y', 'z', 'latitude', 'longitude', 'altitude'])
        
    def close(self):
        """Close the session"""
        self.session.close()
        self.authenticated = False
        self.last_auth_time = None

    def _calculate_position(self, tle_line1, tle_line2, timestamp):
        """
        Calculate satellite position at a given timestamp using TLE data
        
        Args:
            tle_line1: First line of TLE data
            tle_line2: Second line of TLE data
            timestamp: Time at which to calculate position
            
        Returns:
            Tuple containing (x, y, z, lat, lon, alt) or None if calculation fails
        """
        try:
            from sgp4.earth_gravity import wgs84
            from sgp4.io import twoline2rv
            
            # Create satellite object
            satellite = twoline2rv(tle_line1, tle_line2, wgs84)
            
            # Extract time components
            year = timestamp.year
            month = timestamp.month
            day = timestamp.day
            hour = timestamp.hour
            minute = timestamp.minute
            second = timestamp.second
            
            # Calculate position and velocity
            position, velocity = satellite.propagate(
                year, month, day,
                hour, minute, second
            )
            
            if position is None or velocity is None:
                return None
            
            # Convert to geographic coordinates
            from math import degrees, atan2, sqrt, pi
            
            x, y, z = position
            
            # Calculate latitude and longitude
            lat = degrees(atan2(z, sqrt(x*x + y*y)))
            lon = degrees(atan2(y, x)) % 360
            if lon > 180:
                lon -= 360
            
            # Calculate altitude (distance from Earth's center minus Earth's radius)
            alt = sqrt(x*x + y*y + z*z) - 6371  # Earth's mean radius in km
            
            return (x, y, z, lat, lon, alt)
            
        except Exception as e:
            print(f"Error in position calculation: {str(e)}")
            return None

def get_satellite_data(satellite_ids=None, start_date=None, end_date=None, limit=200):
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
            start_date=start_date, 
            end_date=end_date,
            time_step_minutes=5
        )
        
        # Clean up
        client.close()
        
        # Create list of available satellites for selection
        available_satellites = []
        
        # Check if trajectory_df is empty or missing required columns
        if trajectory_df.empty or 'satellite_id' not in trajectory_df.columns or 'object_name' not in trajectory_df.columns:
            print("No trajectory data available to extract satellite information")
            
            # If we have satellite_ids, at least return those
            if satellite_ids:
                for sat_id in satellite_ids:
                    available_satellites.append({
                        'id': str(sat_id),
                        'name': f"Satellite {sat_id}"
                    })
        else:
            # Extract satellite information from trajectory data
            try:
                for sat_id in trajectory_df['satellite_id'].unique():
                    sat_df = trajectory_df[trajectory_df['satellite_id'] == sat_id]
                    if not sat_df.empty and 'object_name' in sat_df.columns:
                        sat_name = sat_df['object_name'].iloc[0]
                        available_satellites.append({
                            'id': sat_id,
                            'name': sat_name
                        })
            except Exception as e:
                print(f"Error extracting satellite information: {e}")
                
        return available_satellites, trajectory_df
        
    except Exception as e:
        print(f"Error fetching satellite data: {e}")
        client.close()
        return [], pd.DataFrame()