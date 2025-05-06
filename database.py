import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

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
    Get list of available satellites from the database.
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        List of satellite IDs
    """
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
        
        # If no results, try alternate table name
        if not satellites:
            alternate_query = text("""
                SELECT DISTINCT satellite_id 
                FROM trajectories 
                ORDER BY satellite_id
            """)
            
            with engine.connect() as conn:
                result = conn.execute(alternate_query)
                satellites = [row[0] for row in result]
                
        return satellites
    
    except Exception as e:
        # If table doesn't exist, try to get information from alerts table
        fallback_query = text("""
            SELECT DISTINCT satellite_id 
            FROM alerts 
            ORDER BY satellite_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(fallback_query)
            satellites = [row[0] for row in result]
            
        return satellites

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
        # If table doesn't exist or query fails
        return ["all"]  # Fallback if query fails

def get_trajectory_data(engine, satellite_id, start_date, end_date, alert_types):
    """
    Get trajectory data for a specific satellite within a date range.
    
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
    
    # If all attempts fail, create a minimal sample DataFrame with expected columns
    # This is empty but has the expected structure
    return pd.DataFrame(columns=[
        'satellite_id', 'timestamp', 'x', 'y', 'z', 
        'velocity_x', 'velocity_y', 'velocity_z',
        'altitude', 'alert_type'
    ])
