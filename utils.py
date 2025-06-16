import pandas as pd
import io
import streamlit as st

def convert_df_to_csv(df):
    """
    Convert DataFrame to CSV string for download.
    
    Args:
        df: Pandas DataFrame to convert
        
    Returns:
        CSV string
    """
    return df.to_csv(index=False).encode('utf-8')

def format_timestamp_column(df):
    """
    Format timestamp column for better display if it exists.
    
    Args:
        df: Pandas DataFrame with timestamp data
        
    Returns:
        DataFrame with formatted timestamp
    """
    if 'timestamp' in df.columns:
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
            # Create a display-friendly timestamp column
            df['timestamp_display'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            # If conversion fails, keep original
            pass
            
    return df

def calculate_earth_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points on Earth surface using Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in degrees
        lat2, lon2: Latitude and longitude of second point in degrees
        
    Returns:
        Distance in kilometers
    """
    import numpy as np
    
    # Convert degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    # Earth radius in kilometers
    earth_radius = 6371.0
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = earth_radius * c
    
    return distance

def detect_coordinate_system(df):
    """
    Try to detect the coordinate system used in the dataframe.
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        String indicating the likely coordinate system
    """
    # Check for common columns
    cartesian = all(col in df.columns for col in ['x', 'y', 'z'])
    latlon = all(col in df.columns for col in ['latitude', 'longitude'])
    
    if cartesian and not latlon:
        return "cartesian"
    elif latlon and not cartesian:
        return "latlon"
    elif cartesian and latlon:
        # Both systems present, need to determine which is the primary
        return "both"
    else:
        return "unknown"

def convert_cartesian_to_spherical(x, y, z):
    """
    Convert Cartesian coordinates to spherical (r, theta, phi).
    
    Args:
        x, y, z: Cartesian coordinates
        
    Returns:
        Tuple of (r, theta, phi) in (meters, radians, radians)
    """
    import numpy as np
    
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(np.sqrt(x**2 + y**2), z)  # Polar angle (latitude)
    phi = np.arctan2(y, x)  # Azimuthal angle (longitude)
    
    return r, theta, phi

def replace_replit_running_icon():
    """Replace Replit running icon with custom icon."""
    pass

def add_custom_css():
    """Add custom CSS to the app."""
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
