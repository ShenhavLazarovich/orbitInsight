import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import traceback
import sqlite3

# Import space_track module with error handling
try:
    # Check if required dependencies are installed
    import sgp4
    SPACE_TRACK_AVAILABLE = True
    print("Space-Track module and dependencies are available.")
except ImportError as e:
    print(f"Space-Track module not available or has dependency issues: {e}")
    traceback.print_exc()
    SPACE_TRACK_AVAILABLE = False

# Import space_track in a function to avoid circular imports
def import_space_track():
    try:
        import space_track as st
        return st
    except ImportError as e:
        print(f"Error importing space_track module: {e}")
        traceback.print_exc()
        return None

def get_database_connection():
    """
    Create a database connection using environment variables.
    Returns a SQLAlchemy engine object.
    """
    # Try to get DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        return create_engine(database_url)
    
    # If DATABASE_URL is not available, try individual connection parameters
    db_host = os.getenv("PGHOST", "localhost")
    db_port = os.getenv("PGPORT", "5432")
    db_name = os.getenv("PGDATABASE", "postgres")
    db_user = os.getenv("PGUSER", "postgres")
    db_password = os.getenv("PGPASSWORD", "")
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_string)

def get_satellites(engine, search_query=None):
    """
    Get list of available satellites from the database or Space-Track API.
    
    Args:
        engine: SQLAlchemy database engine
        search_query: Optional search term to find satellites by name (searches Space-Track if credentials are available)
        
    Returns:
        Dictionary of satellite information with {id: name} pairs, sorted by launch date
    """
    satellites_dict = {}
    
    # First try to get satellites from the local database
    try:
        # Try to get distinct satellite IDs from the trajectories table
        query = text("""
            SELECT DISTINCT satellite_id 
            FROM satellite_trajectories 
            ORDER BY satellite_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            db_satellites = [row[0] for row in result]
            
        # Add database satellites to our dictionary
        if db_satellites:
            print(f"Found {len(db_satellites)} satellites in database: {db_satellites}")
            for sat_id in db_satellites:
                # For database satellites without names, use the ID as the name
                satellites_dict[sat_id] = f"Database Satellite {sat_id}"
                
    except Exception as e:
        print(f"Error querying local database: {e}")
    
    # Add default well-known satellites with their names and approximate launch dates
    default_satellites = {
        "25544": "ISS (International Space Station) (Launched: 1998-11-20)",
        "20580": "Hubble Space Telescope (Launched: 1990-04-24)",
        "41866": "GOES-16 (Geostationary Operational Environmental Satellite) (Launched: 2016-11-19)",
        "39084": "Landsat-8 (Earth Observation Satellite) (Launched: 2013-02-11)",
        "25994": "Terra (Earth Observing System Flagship) (Launched: 1999-12-18)",
        "99001": "OpSat3000 (Earth Observation Satellite) (Launched: 2023-06-15)" # Added OpSat3000 with a unique ID
    }
    
    # Check if we need to populate database with sample data for known satellites
    try:
        # Define satellites to check for
        satellites_to_check = [
            {"id": "20580", "name": "Hubble Space Telescope", "orbit_radius": 6911000, "orbit_period": 95},
            {"id": "99001", "name": "OpSat3000 (Earth Observation Satellite)", "orbit_radius": 7071000, "orbit_period": 100, "alt_variation": 0.1}
        ]
        
        for sat in satellites_to_check:
            sat_id = sat["id"]
            query = text("""
                SELECT COUNT(*) FROM satellite_trajectories 
                WHERE satellite_id = :satellite_id
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {"satellite_id": sat_id})
                count = result.scalar()
                
                # If no data exists for this satellite, add some sample points
                if count == 0:
                    print(f"No data found for {sat['name']}. Adding sample trajectory points.")
                    orbit_radius = sat.get("orbit_radius", 6911000)  # default to Hubble's
                    orbit_period = sat.get("orbit_period", 95)
                    alt_variation = sat.get("alt_variation", 0.05)
                    create_sample_satellite_data(engine, sat_id, sat["name"], orbit_radius, orbit_period, alt_variation)
    except Exception as e:
        print(f"Error checking for Hubble data: {e}")
        # It's okay to continue if this fails
    
    satellite_info_list = []  # Will store satellites with their info for sorting
    
    # Also get satellites from Space-Track API regardless if we found some in the database
    if SPACE_TRACK_AVAILABLE:
        try:
            # Check if we have Space-Track credentials
            if os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD"):
                print("Fetching satellite data from Space-Track.org...")
                
                # Import space_track module dynamically to avoid circular imports
                st = import_space_track()
                if not st:
                    print("Failed to import space_track module")
                    satellite_list = []
                else:
                    # If we have a search query, perform a direct search in SpaceTrack
                    if search_query:
                        print(f"Searching Space-Track for satellites matching: {search_query}")
                        # Create SpaceTrack client instance
                        client = st.SpaceTrackClient()
                        try:
                            # Special handling for common satellites
                            special_cases = {
                                'iss': {'name': 'ISS', 'id': '25544', 'alternative_names': ['ZARYA', 'INTERNATIONAL SPACE STATION']},
                                'hubble': {'name': 'HUBBLE', 'id': '20580', 'alternative_names': ['HST']},
                                'starlink': {'name': 'STARLINK', 'alternative_names': []},
                                'goes': {'name': 'GOES', 'alternative_names': []},
                                'landsat': {'name': 'LANDSAT', 'alternative_names': []},
                                'noaa': {'name': 'NOAA', 'alternative_names': []}
                            }
                            
                            # First check if this is a well-known satellite with special handling
                            search_lower = search_query.lower()
                            satellite_list = []
                            
                            # If special case matches, directly look up satellites by name or ID
                            special_case = None
                            for key, info in special_cases.items():
                                if key in search_lower or search_lower in key:
                                    special_case = info
                                    print(f"Found special case match for '{search_query}': {key} -> {info}")
                                    break
                                    
                            # Add specific handling for OpSat3000
                            if 'opsat' in search_lower:
                                special_case = {'name': 'OPSAT', 'id': '99001', 'alternative_names': ['OPSAT3000', 'OPSAT 3000']}
                                print(f"Special handling for OpSat: {special_case}")
                                
                                # Directly add OpSat3000 to the satellite list as it's our custom satellite
                                satellite_list.append({
                                    'id': '99001',
                                    'name': 'OpSat3000 (Earth Observation Satellite) (Launched: 2023-06-15)',
                                    'launch_date': '2023-06-15'
                                })
                                    
                            if special_case:
                                # For satellites with known IDs, try direct lookup
                                if 'id' in special_case:
                                    try:
                                        print(f"Looking up special case satellite by ID: {special_case['id']}")
                                        tle_by_id = client.get_latest_tle(norad_cat_id=special_case['id'], limit=1)
                                        if not tle_by_id.empty:
                                            # Add this satellite to our list
                                            sat = tle_by_id.iloc[0]
                                            satellite_list.append({
                                                'id': sat['NORAD_CAT_ID'],
                                                'name': f"{sat['OBJECT_NAME']} (NORAD ID: {sat['NORAD_CAT_ID']})",
                                                'launch_date': sat.get('LAUNCH_DATE', 'Unknown')
                                            })
                                    except Exception as e:
                                        print(f"Error looking up special case by ID: {e}")
                                
                                # Try direct name lookup
                                try:
                                    print(f"Looking up special case satellite by name: {special_case['name']}")
                                    # Start with exact match
                                    tle_data = client.get_latest_tle(satellite_name=special_case['name'], limit=100)
                                    # Then try with wildcard
                                    if tle_data.empty:
                                        tle_data = client.get_latest_tle(satellite_name=f"*{special_case['name']}*", limit=100)
                                        
                                    # Try alternative names if needed
                                    for alt_name in special_case['alternative_names']:
                                        if tle_data.empty:
                                            print(f"Trying alternative name: {alt_name}")
                                            tle_alt = client.get_latest_tle(satellite_name=alt_name, limit=100)
                                            if not tle_alt.empty:
                                                tle_data = tle_alt
                                except Exception as e:
                                    print(f"Error in special case lookup: {e}")
                            
                            # Standard search if no special case or special case lookup failed
                            if not satellite_list:
                                # Use wildcard search for the name (add * before and after for SpaceTrack wildcard search)
                                search_pattern = f"*{search_query}*"
                                print(f"Using search pattern: {search_pattern}")
                                tle_data = client.get_latest_tle(satellite_name=search_pattern, limit=500)
                                
                                # Also try direct search if wildcard fails
                                if tle_data.empty:
                                    tle_data = client.get_latest_tle(satellite_name=search_query, limit=500)
                            
                            # Process TLE results
                            if not tle_data.empty:
                                for _, sat in tle_data.iterrows():
                                    if 'NORAD_CAT_ID' in sat and 'OBJECT_NAME' in sat:
                                        # Skip if we already have this satellite in our list
                                        if sat['NORAD_CAT_ID'] in [s.get('id') for s in satellite_list]:
                                            continue
                                            
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
                                        
                                        satellite_list.append({
                                            'id': sat['NORAD_CAT_ID'],
                                            'name': display_name,
                                            'launch_date': launch_date
                                        })
                                print(f"Found {len(satellite_list)} satellites matching '{search_query}' from TLE data")
                            else:
                                print(f"No satellites found from TLE data matching '{search_query}'")
                                
                            # Also search the satellite catalog if we didn't find many results
                            if len(satellite_list) < 50:
                                try:
                                    print("Searching satellite catalog...")
                                    satcat = client.get_satellite_catalog(limit=500)
                                    if not satcat.empty:
                                        # Filter by search term (case-insensitive)
                                        if 'OBJECT_NAME' in satcat.columns:
                                            satcat_filtered = satcat[satcat['OBJECT_NAME'].str.contains(search_query, case=False, na=False)]
                                            
                                            for _, sat in satcat_filtered.iterrows():
                                                if 'NORAD_CAT_ID' in sat and 'OBJECT_NAME' in sat:
                                                    # Skip if we already have this satellite
                                                    if sat['NORAD_CAT_ID'] in [s['id'] for s in satellite_list]:
                                                        continue
                                                        
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
                                                    
                                                    satellite_list.append({
                                                        'id': sat['NORAD_CAT_ID'],
                                                        'name': display_name,
                                                        'launch_date': launch_date
                                                    })
                                        print(f"Total satellites found after catalog search: {len(satellite_list)}")
                                except Exception as e:
                                    print(f"Error searching satellite catalog: {e}")
                                
                        except Exception as search_error:
                            print(f"Error searching SpaceTrack: {search_error}")
                            traceback.print_exc()
                            satellite_list = []
                        finally:
                            client.close()
                    else:
                        # If no search query, use the standard approach to get a list of satellites
                        satellite_list, _ = st.get_satellite_data(limit=200)  # Get more satellites
                
                # Process the results
                if satellite_list:
                    print(f"Found {len(satellite_list)} satellites from Space-Track API")
                    for sat in satellite_list:
                        if 'id' in sat and 'name' in sat:
                            # Add to our structured list for sorting
                            launch_date = sat.get('launch_date', '1900-01-01')  # Default old date if unknown
                            satellite_info_list.append({
                                'id': sat['id'],
                                'name': sat['name'],
                                'launch_date': launch_date
                            })
                else:
                    print("No satellites found from Space-Track API")
                    # Add default satellites if Space-Track returns empty list
                    for sat_id, name in default_satellites.items():
                        # Extract launch date from name for sorting
                        launch_date = '1900-01-01'  # Default
                        if 'Launched:' in name:
                            try:
                                launch_str = name.split('Launched:')[1].strip()
                                launch_date = launch_str.strip('() ')
                            except:
                                pass
                        
                        satellite_info_list.append({
                            'id': sat_id,
                            'name': name,
                            'launch_date': launch_date
                        })
                
        except Exception as e:
            print(f"Error fetching from Space-Track API: {e}")
            traceback.print_exc()
            # Add default satellites if Space-Track fails
            for sat_id, name in default_satellites.items():
                # Extract launch date from name for sorting
                launch_date = '1900-01-01'  # Default
                if 'Launched:' in name:
                    try:
                        launch_str = name.split('Launched:')[1].strip()
                        launch_date = launch_str.strip('() ')
                    except:
                        pass
                
                satellite_info_list.append({
                    'id': sat_id,
                    'name': name,
                    'launch_date': launch_date
                })
    else:
        print("Space-Track module is not available, using default satellite list")
        # Add default satellites if Space-Track not available
        for sat_id, name in default_satellites.items():
            # Extract launch date from name for sorting
            launch_date = '1900-01-01'  # Default
            if 'Launched:' in name:
                try:
                    launch_str = name.split('Launched:')[1].strip()
                    launch_date = launch_str.strip('() ')
                except:
                    pass
            
            satellite_info_list.append({
                'id': sat_id,
                'name': name,
                'launch_date': launch_date
            })
    
    # Add database satellites to the list too (with default launch date for sorting)
    for sat_id, name in satellites_dict.items():
        # Skip if already in the list
        if sat_id in [s['id'] for s in satellite_info_list]:
            continue
            
        satellite_info_list.append({
            'id': sat_id,
            'name': name,
            'launch_date': '1900-01-01'  # Default old date for unknown database satellites
        })
    
    # Sort by launch date (newest first)
    try:
        # Convert dates to sortable format and sort
        satellite_info_list.sort(
            key=lambda x: pd.to_datetime(x['launch_date'], errors='coerce') 
                          or pd.Timestamp('1900-01-01'),  # Handle invalid dates
            reverse=True  # Newest first
        )
    except Exception as e:
        print(f"Error sorting satellites by launch date: {e}")
        traceback.print_exc()
    
    # Convert sorted list back to dictionary
    satellites_dict = {sat['id']: sat['name'] for sat in satellite_info_list}
    
    # If we still have no satellites, use the default list
    if not satellites_dict:
        print("No satellites found, using default list")
        satellites_dict = default_satellites
        
    print(f"Returning {len(satellites_dict)} satellites")
    return satellites_dict

def get_space_track_data(engine, data_type, days_back=30, limit=100):
    """
    Get data from Space-Track API for a specific data type.
    
    Args:
        engine: SQLAlchemy database engine
        data_type: Type of data to retrieve (e.g., "catalog", "launch_sites", "decay", "conjunction", "boxscore")
        days_back: Number of days in the past to retrieve data for (for time-based queries)
        limit: Maximum number of results to return
        
    Returns:
        Pandas DataFrame with the requested data
    """
    if not SPACE_TRACK_AVAILABLE:
        print("Space-Track module is not available.")
        return pd.DataFrame()
    
    # Check if we have Space-Track credentials
    if not (os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD")):
        print("Space-Track credentials not found. Please set SPACETRACK_USERNAME and SPACETRACK_PASSWORD")
        return pd.DataFrame()
    
    # Import space_track module dynamically to avoid circular imports
    st = import_space_track()
    if not st:
        print("Failed to import space_track module")
        return pd.DataFrame()
    
    try:
        # Initialize Space-Track client
        client = st.SpaceTrackClient()
        
        # Get data based on the requested type
        if data_type == "catalog":
            df = client.get_satellite_catalog(limit=limit)
        elif data_type == "launch_sites":
            df = client.get_launch_sites(limit=limit)
        elif data_type == "decay":
            df = client.get_decay_data(days_back=days_back, limit=limit)
        elif data_type == "conjunction":
            df = client.get_conjunction_data(days_back=days_back, limit=limit)
            
            # Add standardized column names for visualization if data was found
            if not df.empty:
                # Map common column names to our standardized ones for visualization
                column_mapping = {
                    # Time columns
                    'TCA': 'CDM_TCA',
                    'CLOSEST_APPROACH_TIME': 'CDM_TCA',
                    'CONJUNCTION_TIME': 'CDM_TCA',
                    
                    # Distance columns
                    'MIN_RNG': 'MISS_DISTANCE',
                    'RANGE': 'MISS_DISTANCE',
                    'MINIMUM_RANGE': 'MISS_DISTANCE',
                    'CLOSE_APPROACH_DIST': 'MISS_DISTANCE',
                    
                    # Speed columns
                    'REL_SPEED': 'RELATIVE_SPEED',
                    'RELATIVE_VELOCITY': 'RELATIVE_SPEED',
                    'V_REL': 'RELATIVE_SPEED',
                    
                    # Probability columns
                    'COLLISION_PROBABILITY': 'PC',
                    'PROB': 'PC',
                    'PROBABILITY': 'PC',
                    
                    # Object columns
                    'OBJECT': 'OBJECT_NAME',
                    'PRIMARY_OBJECT': 'OBJECT_NAME',
                    'OBJECT_DESIGNATOR': 'OBJECT_ID',
                    'SAT_1_NAME': 'OBJECT_NAME',
                    'SAT_2_NAME': 'OBJECT_2_NAME'
                }
                
                # Apply mapping (only for columns that exist in the dataframe)
                for orig_col, new_col in column_mapping.items():
                    if orig_col in df.columns and new_col not in df.columns:
                        df[new_col] = df[orig_col]
                
                # Print column names for debugging
                print(f"Conjunction data columns after mapping: {df.columns.tolist()}")
        elif data_type == "boxscore":
            df = client.get_boxscore_data(limit=limit)
        else:
            print(f"Unknown data type: {data_type}")
            return pd.DataFrame()
        
        # Close the client connection
        client.close()
        
        return df
    
    except Exception as e:
        print(f"Error fetching data from Space-Track API: {e}")
        traceback.print_exc()
        return pd.DataFrame()

def get_alert_types(engine):
    """
    Get list of available alert types from the database.
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        List of alert types
    """
    try:
        query = text("""
            SELECT DISTINCT alert_type 
            FROM alerts 
            ORDER BY alert_type
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            alert_types = [row[0] for row in result]
        
        if not alert_types:
            return ["all"]  # Fallback if no alert types found
            
        return alert_types
    
    except Exception:
        # If table doesn't exist or query fails, return default alert types
        return ["all", "PROXIMITY_WARNING", "TRAJECTORY_DEVIATION", "RADIATION_HAZARD", "LOW_POWER"]

def get_trajectory_data(engine, satellite_id, start_date, end_date, alert_types):
    """
    Get trajectory data for a specific satellite within a date range.
    Tries local database first, then Space-Track API if necessary.
    
    Args:
        engine: SQLAlchemy database engine
        satellite_id: ID of the satellite
        start_date: Start date for filtering
        end_date: End date for filtering
        alert_types: List of alert types to include
        
    Returns:
        Pandas DataFrame with trajectory data
    """
    # Special case handling for OpSat3000
    if satellite_id == "99001":
        print("OpSat3000 selected - checking for sample trajectory data")
        # Check if we already have data for this satellite
        try:
            # First check if data exists in the database
            query = text("""
                SELECT COUNT(*) FROM satellite_trajectories 
                WHERE satellite_id = :satellite_id
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {"satellite_id": satellite_id})
                count = result.scalar()
                
            # If no data exists, create sample data
            if count == 0:
                print("No data found for OpSat3000. Creating sample trajectory points.")
                create_sample_satellite_data(
                    engine, 
                    "99001", 
                    "OpSat3000 (Earth Observation Satellite)", 
                    7071000,  # orbit_radius (700 km altitude)
                    100,      # orbit_period in minutes
                    0.1       # altitude variation
                )
        except Exception as e:
            print(f"Error checking for OpSat3000 data: {e}")
            traceback.print_exc()
            
    # First try local database
    db_data = get_trajectory_data_from_db(engine, satellite_id, start_date, end_date, alert_types)
    
    # If we got data from the database, return it
    if not db_data.empty:
        return db_data
    
    # If no data in database, try Space-Track API if available
    print(f"No data found in local database for satellite {satellite_id}.")
    
    if not SPACE_TRACK_AVAILABLE:
        print("Space-Track module is not available.")
        return pd.DataFrame(columns=[
            'satellite_id', 'timestamp', 'x', 'y', 'z', 
            'velocity_x', 'velocity_y', 'velocity_z',
            'altitude', 'alert_type'
        ])
    
    print("Trying Space-Track API...")
        
    # Check if we have Space-Track credentials
    if not (os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD")):
        print("Space-Track credentials not found. Please set SPACETRACK_USERNAME and SPACETRACK_PASSWORD")
        return pd.DataFrame(columns=[
            'satellite_id', 'timestamp', 'x', 'y', 'z', 
            'velocity_x', 'velocity_y', 'velocity_z',
            'altitude', 'alert_type'
        ])
    
    try:
        # Import space_track module dynamically
        st = import_space_track()
        if not st:
            print("Failed to import space_track module")
            return pd.DataFrame()
        
        # Get trajectory data from Space-Track
        _, trajectory_df = st.get_satellite_data(
            satellite_ids=[satellite_id],
            start_date=start_date,
            end_date=end_date
        )
        
        if not trajectory_df.empty:
            # Format the data for our application
            trajectory_df = trajectory_df.rename(columns={'object_name': 'satellite_name'})
            
            # Add alert_type column if it doesn't exist (default to None)
            if 'alert_type' not in trajectory_df.columns:
                trajectory_df['alert_type'] = None
            
            # Store the data in the database for future use
            store_trajectory_data(engine, trajectory_df)
            
            return trajectory_df
            
    except Exception as e:
        print(f"Error fetching from Space-Track API: {e}")
        traceback.print_exc()
    
    # If all attempts fail, return empty DataFrame with expected structure
    return pd.DataFrame(columns=[
        'satellite_id', 'timestamp', 'x', 'y', 'z', 
        'velocity_x', 'velocity_y', 'velocity_z',
        'altitude', 'alert_type'
    ])

def get_trajectory_data_from_db(engine, satellite_id, start_date, end_date, alert_types):
    """
    Get trajectory data from the local database.
    
    Args:
        engine: SQLAlchemy database engine
        satellite_id: ID of the satellite
        start_date: Start date for filtering
        end_date: End date for filtering
        alert_types: List of alert types to include
        
    Returns:
        Pandas DataFrame with trajectory data
    """
    # Convert dates to strings for SQL
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = (end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")  # Include end_date in range
    
    # Build SQL query - try to handle different possible schema structures
    try:
        # First, try the most likely table structure
        query = text(f"""
            SELECT t.*, a.alert_type
            FROM satellite_trajectories t
            LEFT JOIN alerts a ON t.satellite_id = a.satellite_id AND DATE(t.timestamp) = DATE(a.timestamp)
            WHERE t.satellite_id = :satellite_id
            AND t.timestamp BETWEEN :start_date AND :end_date
            {'AND a.alert_type IN :alert_types' if 'all' not in alert_types else ''}
            ORDER BY t.timestamp
        """)
        
        with engine.connect() as conn:
            result = pd.read_sql(
                query, 
                conn, 
                params={
                    "satellite_id": satellite_id,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "alert_types": tuple(alert_types) if len(alert_types) > 1 else f"('{alert_types[0]}')"
                }
            )
        
        # If the query returned data, return it
        if not result.empty:
            return result
            
    except Exception:
        # If the first query fails, try an alternate table structure
        pass
    
    try:
        # Try a simpler query with just trajectories table
        query = text(f"""
            SELECT *
            FROM trajectories
            WHERE satellite_id = :satellite_id
            AND timestamp BETWEEN :start_date AND :end_date
            ORDER BY timestamp
        """)
        
        with engine.connect() as conn:
            result = pd.read_sql(
                query, 
                conn, 
                params={
                    "satellite_id": satellite_id,
                    "start_date": start_date_str,
                    "end_date": end_date_str
                }
            )
        
        return result
            
    except Exception:
        # If both queries fail, try to determine the table structure and create a new query
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        with engine.connect() as conn:
            tables_result = conn.execute(tables_query)
            tables = [row[0] for row in tables_result]
        
        # Look for tables related to satellites or trajectories
        trajectory_tables = [table for table in tables if 'trajectory' in table or 'satellite' in table]
        
        if trajectory_tables:
            # Use the first matching table
            table_name = trajectory_tables[0]
            
            # Get the columns in this table
            columns_query = text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            
            with engine.connect() as conn:
                columns_result = conn.execute(columns_query)
                columns = [row[0] for row in columns_result]
            
            # Check if the table has necessary columns
            if 'satellite_id' in columns and ('timestamp' in columns or 'time' in columns):
                time_column = 'timestamp' if 'timestamp' in columns else 'time'
                
                query = text(f"""
                    SELECT * 
                    FROM {table_name}
                    WHERE satellite_id = :satellite_id
                    AND {time_column} BETWEEN :start_date AND :end_date
                    ORDER BY {time_column}
                """)
                
                with engine.connect() as conn:
                    result = pd.read_sql(
                        query, 
                        conn, 
                        params={
                            "satellite_id": satellite_id,
                            "start_date": start_date_str,
                            "end_date": end_date_str
                        }
                    )
                
                return result
    
    # Return empty DataFrame if no data found
    return pd.DataFrame()

def create_sample_satellite_data(engine, satellite_id, satellite_name, orbit_radius, orbit_period=95, alt_variation=0.05):
    """
    Create sample trajectory data for a satellite.
    This is used as a fallback when Space-Track API doesn't return data.
    
    Args:
        engine: SQLAlchemy database engine
        satellite_id: ID of the satellite to create data for
        satellite_name: Name of the satellite
        orbit_radius: Radius of the orbit in meters (Earth radius + altitude)
        orbit_period: Orbit period in minutes (default: 95)
        alt_variation: Variation in altitude as a fraction of orbit_radius (default: 0.05)
    """
    try:
        # First, check if the table exists
        check_table_query = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'satellite_trajectories'
            )
        """)
        
        with engine.connect() as conn:
            result = conn.execute(check_table_query)
            table_exists = result.scalar()
        
        if table_exists:
            # Check if satellite_name column exists
            check_column_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'satellite_trajectories' AND column_name = 'satellite_name'
                )
            """)
            
            with engine.connect() as conn:
                result = conn.execute(check_column_query)
                column_exists = result.scalar()
            
            # If the column doesn't exist, add it
            if not column_exists:
                alter_table_query = text("""
                    ALTER TABLE satellite_trajectories 
                    ADD COLUMN satellite_name VARCHAR(100)
                """)
                
                with engine.connect() as conn:
                    conn.execute(alter_table_query)
                    conn.commit()
                    print("Added satellite_name column to existing table")
        else:
            # Create the satellite_trajectories table with all columns
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS satellite_trajectories (
                    id SERIAL PRIMARY KEY,
                    satellite_id VARCHAR(50) NOT NULL,
                    satellite_name VARCHAR(100),
                    timestamp TIMESTAMP NOT NULL,
                    x FLOAT,
                    y FLOAT,
                    z FLOAT,
                    velocity_x FLOAT,
                    velocity_y FLOAT,
                    velocity_z FLOAT,
                    altitude FLOAT
                )
            """)
            
            with engine.connect() as conn:
                conn.execute(create_table_query)
                conn.commit()
                print("Created satellite_trajectories table")
                
        # Check if we already have data for this satellite
        check_data_query = text("""
            SELECT COUNT(*) FROM satellite_trajectories 
            WHERE satellite_id = :satellite_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(check_data_query, {"satellite_id": satellite_id})
            data_count = result.scalar()
            
        if data_count > 0:
            print(f"Data for satellite {satellite_id} already exists in database. Skipping sample data creation.")
            return
            
        # Generate sample trajectory data
        import math
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate data points for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Generate one point every 30 minutes
        time_points = []
        current_time = start_date
        while current_time <= end_date:
            time_points.append(current_time)
            current_time += timedelta(minutes=30)
        
        # Generate trajectory points
        trajectory_data = []
        for i, timestamp in enumerate(time_points):
            # Calculate position using simple circular orbit model
            elapsed_minutes = (timestamp - start_date).total_seconds() / 60
            orbit_angle = (elapsed_minutes % orbit_period) * (2 * math.pi / orbit_period)
            
            # Add some eccentricity to make it more realistic
            x = orbit_radius * math.cos(orbit_angle)
            y = orbit_radius * math.sin(orbit_angle)
            z = orbit_radius * 0.1 * math.sin(orbit_angle * 2)  # Slight inclination
            
            # Add some random variation in the orbit radius to simulate altitude changes
            variation = orbit_radius * alt_variation * math.sin(orbit_angle * 8)
            x += variation * math.cos(orbit_angle)
            y += variation * math.sin(orbit_angle)
            
            # Calculate velocity (approximately 7.5 km/s for this orbit)
            velocity_magnitude = 7500  # m/s
            vx = -velocity_magnitude * math.sin(orbit_angle)
            vy = velocity_magnitude * math.cos(orbit_angle)
            vz = velocity_magnitude * 0.1 * math.cos(orbit_angle * 2)
            
            # Add some random variation to make it look more realistic
            random_factor = 0.01  # 1% variation
            x = x * (1 + random_factor * (np.random.random() - 0.5))
            y = y * (1 + random_factor * (np.random.random() - 0.5))
            z = z * (1 + random_factor * (np.random.random() - 0.5))
            
            # Calculate altitude
            altitude = math.sqrt(x**2 + y**2 + z**2) - 6371000  # Earth radius in meters
            
            trajectory_data.append((
                satellite_id, 
                satellite_name, 
                timestamp,
                x, y, z,
                vx, vy, vz,
                altitude
            ))
        
        # Insert data into the database
        insert_query = text("""
            INSERT INTO satellite_trajectories 
            (satellite_id, satellite_name, timestamp, x, y, z, velocity_x, velocity_y, velocity_z, altitude)
            VALUES (:satellite_id, :satellite_name, :timestamp, :x, :y, :z, :vx, :vy, :vz, :altitude)
        """)
        
        with engine.connect() as conn:
            for point in trajectory_data:
                conn.execute(insert_query, {
                    "satellite_id": point[0],
                    "satellite_name": point[1],
                    "timestamp": point[2],
                    "x": point[3],
                    "y": point[4],
                    "z": point[5],
                    "vx": point[6],
                    "vy": point[7],
                    "vz": point[8],
                    "altitude": point[9]
                })
            conn.commit()
        
        print(f"Added {len(trajectory_data)} sample trajectory points for {satellite_name}")
        
    except Exception as e:
        print(f"Error creating sample data for {satellite_name}: {e}")
        traceback.print_exc()

def store_trajectory_data(engine, trajectory_df):
    """
    Store trajectory data in the local database for future use.
    
    Args:
        engine: SQLAlchemy database engine
        trajectory_df: DataFrame with trajectory data
    """
    if trajectory_df.empty:
        return
        
    try:
        # First, check if the table exists
        check_table_query = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'satellite_trajectories'
            )
        """)
        
        with engine.connect() as conn:
            result = conn.execute(check_table_query)
            table_exists = result.scalar()
        
        if table_exists:
            # Check if satellite_name column exists
            check_column_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'satellite_trajectories' AND column_name = 'satellite_name'
                )
            """)
            
            with engine.connect() as conn:
                result = conn.execute(check_column_query)
                column_exists = result.scalar()
            
            # If the column doesn't exist, add it
            if not column_exists:
                alter_table_query = text("""
                    ALTER TABLE satellite_trajectories 
                    ADD COLUMN satellite_name VARCHAR(100)
                """)
                
                with engine.connect() as conn:
                    conn.execute(alter_table_query)
                    conn.commit()
                    print("Added satellite_name column to existing table")
        else:
            # Create the satellite_trajectories table with all columns
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS satellite_trajectories (
                    id SERIAL PRIMARY KEY,
                    satellite_id VARCHAR(50) NOT NULL,
                    satellite_name VARCHAR(100),
                    timestamp TIMESTAMP NOT NULL,
                    x FLOAT,
                    y FLOAT,
                    z FLOAT,
                    velocity_x FLOAT,
                    velocity_y FLOAT,
                    velocity_z FLOAT,
                    altitude FLOAT
                )
            """)
            
            with engine.connect() as conn:
                conn.execute(create_table_query)
                conn.commit()
                print("Created satellite_trajectories table")
        
        # Prepare DataFrame for storage
        df_to_store = trajectory_df.copy()
        
        # Keep only the columns we want to store
        columns_to_keep = [
            'satellite_id', 'satellite_name', 'timestamp', 
            'x', 'y', 'z', 'velocity_x', 'velocity_y', 'velocity_z', 'altitude'
        ]
        
        # Keep only columns that exist in the DataFrame
        columns_to_keep = [col for col in columns_to_keep if col in df_to_store.columns]
        
        # Store in database
        df_to_store[columns_to_keep].to_sql(
            'satellite_trajectories', 
            engine, 
            if_exists='append', 
            index=False
        )
        
        print(f"Stored {len(df_to_store)} trajectory points in the database")
        
    except Exception as e:
        print(f"Error storing trajectory data in database: {e}")

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect('orbitinsight.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password_hash TEXT,
                  email TEXT,
                  created_at TIMESTAMP)''')
    
    # Create feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  feedback_type TEXT,
                  message TEXT,
                  created_at TIMESTAMP,
                  status TEXT DEFAULT 'pending')''')
    
    # Create satellites table
    c.execute('''CREATE TABLE IF NOT EXISTS satellites
                 (norad_id INTEGER PRIMARY KEY,
                  name TEXT,
                  country TEXT,
                  launch_date TIMESTAMP,
                  status TEXT,
                  altitude REAL,
                  inclination REAL)''')
    
    # Create launch_sites table
    c.execute('''CREATE TABLE IF NOT EXISTS launch_sites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  country TEXT,
                  location TEXT,
                  status TEXT,
                  launch_count INTEGER,
                  first_launch TIMESTAMP,
                  last_launch TIMESTAMP)''')
    
    # Create decay_events table
    c.execute('''CREATE TABLE IF NOT EXISTS decay_events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  norad_id INTEGER,
                  name TEXT,
                  country TEXT,
                  decay_date TIMESTAMP,
                  pre_decay_altitude REAL,
                  prediction_accuracy REAL)''')
    
    # Create conjunction_events table
    c.execute('''CREATE TABLE IF NOT EXISTS conjunction_events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  satellite1_id INTEGER,
                  satellite1_name TEXT,
                  satellite2_id INTEGER,
                  satellite2_name TEXT,
                  time_of_closest_approach TIMESTAMP,
                  miss_distance REAL,
                  probability REAL)''')
    
    conn.commit()
    conn.close()

def search_satellites(search_term):
    """Search satellites by name or NORAD ID."""
    conn = get_db_connection()
    query = '''SELECT * FROM satellites 
               WHERE name LIKE ? OR norad_id LIKE ?
               LIMIT 10'''
    results = conn.execute(query, (f'%{search_term}%', f'%{search_term}%')).fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_satellite_trajectory(norad_id, start_date, end_date, alert_types):
    """Get satellite trajectory data."""
    # Placeholder for trajectory data
    # In a real implementation, this would query a trajectory database
    return pd.DataFrame({
        'timestamp': pd.date_range(start_date, end_date, freq='1min'),
        'x': [0] * 1000,  # Placeholder values
        'y': [0] * 1000,
        'z': [0] * 1000,
        'altitude': [400] * 1000
    })

def get_catalog_data(search_term=None, countries=None, status=None, launch_year_range=None):
    """Get satellite catalog data with filters."""
    conn = get_db_connection()
    query = 'SELECT * FROM satellites WHERE 1=1'
    params = []
    
    if search_term:
        query += ' AND (name LIKE ? OR norad_id LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    if countries:
        placeholders = ','.join(['?'] * len(countries))
        query += f' AND country IN ({placeholders})'
        params.extend(countries)
    
    if status:
        placeholders = ','.join(['?'] * len(status))
        query += f' AND status IN ({placeholders})'
        params.extend(status)
    
    if launch_year_range:
        query += ' AND strftime("%Y", launch_date) BETWEEN ? AND ?'
        params.extend([str(launch_year_range[0]), str(launch_year_range[1])])
    
    results = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results

def get_launch_sites_data(search_term=None, countries=None, status=None, min_launches=0):
    """Get launch sites data with filters."""
    conn = get_db_connection()
    query = 'SELECT * FROM launch_sites WHERE 1=1'
    params = []
    
    if search_term:
        query += ' AND (name LIKE ? OR location LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    if countries:
        placeholders = ','.join(['?'] * len(countries))
        query += f' AND country IN ({placeholders})'
        params.extend(countries)
    
    if status:
        placeholders = ','.join(['?'] * len(status))
        query += f' AND status IN ({placeholders})'
        params.extend(status)
    
    if min_launches > 0:
        query += ' AND launch_count >= ?'
        params.append(min_launches)
    
    results = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results

def get_decay_data(search_term=None, countries=None, date_range=None, min_altitude=0):
    """Get decay events data with filters."""
    conn = get_db_connection()
    query = 'SELECT * FROM decay_events WHERE 1=1'
    params = []
    
    if search_term:
        query += ' AND (name LIKE ? OR norad_id LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    if countries:
        placeholders = ','.join(['?'] * len(countries))
        query += f' AND country IN ({placeholders})'
        params.extend(countries)
    
    if date_range:
        query += ' AND decay_date BETWEEN ? AND ?'
        params.extend([date_range[0], date_range[1]])
    
    if min_altitude > 0:
        query += ' AND pre_decay_altitude >= ?'
        params.append(min_altitude)
    
    results = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results

def get_conjunction_data(search_term=None, min_probability=0, date_range=None, min_distance=0):
    """Get conjunction events data with filters."""
    conn = get_db_connection()
    query = 'SELECT * FROM conjunction_events WHERE 1=1'
    params = []
    
    if search_term:
        query += ''' AND (satellite1_name LIKE ? 
                         OR satellite2_name LIKE ? 
                         OR satellite1_id LIKE ? 
                         OR satellite2_id LIKE ?)'''
        params.extend([f'%{search_term}%'] * 4)
    
    if min_probability > 0:
        query += ' AND probability >= ?'
        params.append(min_probability)
    
    if date_range:
        query += ' AND time_of_closest_approach BETWEEN ? AND ?'
        params.extend([date_range[0], date_range[1]])
    
    if min_distance > 0:
        query += ' AND miss_distance >= ?'
        params.append(min_distance)
    
    results = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results

def get_boxscore_data(countries=None, time_period=None):
    """Get boxscore statistics data."""
    conn = get_db_connection()
    
    # Calculate date range based on time period
    end_date = datetime.now()
    if time_period == "Last 30 Days":
        start_date = end_date - timedelta(days=30)
    elif time_period == "Last 90 Days":
        start_date = end_date - timedelta(days=90)
    elif time_period == "Last Year":
        start_date = end_date - timedelta(days=365)
    else:  # All Time
        start_date = datetime(1957, 1, 1)  # Start of space age
    
    query = '''SELECT 
                  country,
                  COUNT(*) as total_objects,
                  SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_satellites,
                  SUM(CASE WHEN status = 'Debris' THEN 1 ELSE 0 END) as debris,
                  SUM(CASE WHEN type = 'Payload' THEN 1 ELSE 0 END) as payloads,
                  SUM(CASE WHEN type = 'Rocket Body' THEN 1 ELSE 0 END) as rocket_bodies,
                  COUNT(DISTINCT launch_date) as launches
               FROM satellites
               WHERE launch_date BETWEEN ? AND ?'''
    params = [start_date, end_date]
    
    if countries:
        placeholders = ','.join(['?'] * len(countries))
        query += f' AND country IN ({placeholders})'
        params.extend(countries)
    
    query += ' GROUP BY country'
    
    results = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results
