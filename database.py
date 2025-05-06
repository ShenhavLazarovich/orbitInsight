import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import space_track as st

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

def get_satellites(engine):
    """
    Get list of available satellites from the database or Space-Track API.
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        List of satellite IDs
    """
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
            satellites = [row[0] for row in result]
        
        # If we found satellites in the database, return them
        if satellites:
            return satellites
                
    except Exception as e:
        print(f"Error querying local database: {e}")
    
    # If no satellites found in the database, try to fetch from Space-Track API
    try:
        # Check if we have Space-Track credentials
        if os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD"):
            print("Fetching satellite data from Space-Track.org...")
            
            # Get satellite data from Space-Track
            satellite_list, _ = st.get_satellite_data(limit=20)
            
            # Extract just the IDs
            if satellite_list:
                return [sat['id'] for sat in satellite_list]
            
    except Exception as e:
        print(f"Error fetching from Space-Track API: {e}")
    
    # If nothing worked, return a default list of known NORAD IDs
    # ISS, Hubble, GOES-16, Landsat-8, Terra
    return ["25544", "20580", "41866", "39084", "25994"]

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
    # First try local database
    db_data = get_trajectory_data_from_db(engine, satellite_id, start_date, end_date, alert_types)
    
    # If we got data from the database, return it
    if not db_data.empty:
        return db_data
    
    # If no data in database, try Space-Track API
    print(f"No data found in local database for satellite {satellite_id}. Trying Space-Track API...")
    
    # Check if we have Space-Track credentials
    if not (os.getenv("SPACETRACK_USERNAME") and os.getenv("SPACETRACK_PASSWORD")):
        print("Space-Track credentials not found. Please set SPACETRACK_USERNAME and SPACETRACK_PASSWORD")
        return pd.DataFrame(columns=[
            'satellite_id', 'timestamp', 'x', 'y', 'z', 
            'velocity_x', 'velocity_y', 'velocity_z',
            'altitude', 'alert_type'
        ])
    
    try:
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
        # Ensure the satellite_trajectories table exists
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
