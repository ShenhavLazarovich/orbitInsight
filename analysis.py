import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from datetime import datetime, timedelta

def calculate_basic_stats(df):
    """
    Calculate basic statistics for numerical columns in the dataframe.
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        DataFrame with basic statistics
    """
    # Calculate statistics
    stats_df = df.describe().T
    
    # Add more statistics
    stats_df['median'] = df.median()
    stats_df['skewness'] = df.skew()
    stats_df['kurtosis'] = df.kurtosis()
    
    # Reorder columns for better readability
    cols_order = ['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max', 'skewness', 'kurtosis']
    stats_df = stats_df[cols_order]
    
    # Round values for better display
    stats_df = stats_df.round(4)
    
    return stats_df

def calculate_trajectory_metrics(df):
    """
    Calculate key metrics about the satellite trajectory.
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        Dictionary with trajectory metrics
    """
    metrics = {}
    
    # Ensure data is sorted by timestamp
    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp')
        
    # Calculate total distance traveled
    # First, check if we have position coordinates
    if all(col in df.columns for col in ['x', 'y', 'z']):
        # Calculate distance between consecutive points
        df['dx'] = df['x'].diff()
        df['dy'] = df['y'].diff()
        df['dz'] = df['z'].diff()
        
        # Calculate distance for each step
        df['distance'] = np.sqrt(df['dx']**2 + df['dy']**2 + df['dz']**2)
        
        # Total distance (in km if coordinates are in m)
        metrics['total_distance'] = df['distance'].sum() / 1000 
    else:
        metrics['total_distance'] = 0
    
    # Calculate duration
    if 'timestamp' in df.columns:
        try:
            duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600  # in hours
            metrics['duration'] = duration
        except:
            # Handle case where timestamp is not datetime
            metrics['duration'] = 0
    else:
        metrics['duration'] = 0
    
    # Average speed (km/h)
    if metrics['duration'] > 0:
        metrics['avg_speed'] = metrics['total_distance'] / metrics['duration']
    else:
        metrics['avg_speed'] = 0
    
    # Altitude metrics
    if 'altitude' in df.columns:
        metrics['max_altitude'] = df['altitude'].max() / 1000  # in km if altitude is in m
        metrics['min_altitude'] = df['altitude'].min() / 1000
    else:
        metrics['max_altitude'] = 0
        metrics['min_altitude'] = 0
    
    # Count of alerts
    if 'alert_type' in df.columns:
        alerts = df[df['alert_type'].notna()]
        metrics['alerts_count'] = len(alerts)
    else:
        metrics['alerts_count'] = 0
    
    return metrics

def plot_alert_distribution(df):
    """
    Create a plot showing distribution of alert types.
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        Plotly figure object
    """
    if 'alert_type' not in df.columns or df['alert_type'].isna().all():
        # Create an empty figure if no alert data
        fig = go.Figure()
        fig.update_layout(
            title="No Alert Data Available",
            xaxis_title="Alert Type",
            yaxis_title="Count"
        )
        return fig
    
    # Count alerts by type
    alert_counts = df['alert_type'].value_counts().reset_index()
    alert_counts.columns = ['Alert Type', 'Count']
    
    # Create bar chart
    fig = px.bar(
        alert_counts, 
        x='Alert Type', 
        y='Count',
        title='Distribution of Alert Types',
        color='Alert Type'
    )
    
    return fig

def detect_anomalies(df, parameter, threshold=3.0):
    """
    Detect anomalies in a parameter using Z-score method.
    
    Args:
        df: Pandas DataFrame with trajectory data
        parameter: Column name to analyze for anomalies
        threshold: Z-score threshold for anomaly detection
        
    Returns:
        Tuple of (DataFrame with anomalies, Plotly figure)
    """
    if parameter not in df.columns or df[parameter].isna().all():
        # Return empty dataframe and figure if parameter doesn't exist
        empty_df = pd.DataFrame(columns=df.columns)
        fig = go.Figure()
        fig.update_layout(title=f"No data available for {parameter}")
        return empty_df, fig
    
    # Calculate Z-scores
    z_scores = np.abs(stats.zscore(df[parameter].fillna(df[parameter].mean())))
    
    # Identify anomalies
    anomalies = z_scores > threshold
    anomaly_df = df[anomalies].copy()
    
    # Create figure
    fig = go.Figure()
    
    # Add regular points
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[parameter],
        mode='lines+markers',
        name=parameter,
        marker=dict(size=6)
    ))
    
    # Add anomalies
    if not anomaly_df.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_df.index,
            y=anomaly_df[parameter],
            mode='markers',
            name='Anomalies',
            marker=dict(
                color='red',
                size=10,
                symbol='circle-open',
                line=dict(width=2)
            )
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Anomaly Detection for {parameter} (Z-score threshold: {threshold})",
        xaxis_title="Data Point",
        yaxis_title=parameter,
        legend_title="Legend"
    )
    
    return anomaly_df, fig

def analyze_trajectory(trajectory_data):
    """Analyze satellite trajectory data."""
    # Calculate basic orbital parameters
    avg_altitude = trajectory_data['altitude'].mean()
    
    # Calculate orbital period (assuming circular orbit)
    # Using Kepler's Third Law: T = 2π * sqrt(a³/μ)
    # where a is semi-major axis and μ is Earth's gravitational parameter
    earth_radius = 6371  # km
    mu = 398600.4418  # km³/s²
    a = avg_altitude + earth_radius
    orbital_period = 2 * np.pi * np.sqrt(a**3 / mu) / 60  # Convert to minutes
    
    # Calculate eccentricity (simplified)
    eccentricity = 0.0  # Placeholder for circular orbit
    
    # Calculate inclination (simplified)
    inclination = 0.0  # Placeholder
    
    return {
        'avg_altitude': avg_altitude,
        'orbital_period': orbital_period,
        'eccentricity': eccentricity,
        'inclination': inclination
    }

def analyze_catalog(catalog_data):
    """Analyze satellite catalog data."""
    analysis = {
        'total_satellites': len(catalog_data),
        'active_satellites': len(catalog_data[catalog_data['status'] == 'Active']),
        'countries': catalog_data['country'].nunique(),
        'launch_years': catalog_data['launch_date'].dt.year.nunique(),
        'avg_altitude': catalog_data['altitude'].mean(),
        'avg_inclination': catalog_data['inclination'].mean()
    }
    return analysis

def analyze_launch_sites(launch_sites_data):
    """Analyze launch sites data."""
    analysis = {
        'total_sites': len(launch_sites_data),
        'active_sites': len(launch_sites_data[launch_sites_data['status'] == 'Active']),
        'total_launches': launch_sites_data['launch_count'].sum(),
        'countries': launch_sites_data['country'].nunique(),
        'avg_launches_per_site': launch_sites_data['launch_count'].mean()
    }
    return analysis

def analyze_decay_events(decay_data):
    """Analyze decay events data."""
    analysis = {
        'total_decays': len(decay_data),
        'avg_altitude': decay_data['pre_decay_altitude'].mean(),
        'avg_prediction_accuracy': decay_data['prediction_accuracy'].mean(),
        'countries': decay_data['country'].nunique(),
        'recent_decays': len(decay_data[decay_data['decay_date'] > datetime.now() - timedelta(days=30)])
    }
    return analysis

def analyze_conjunction_events(conjunction_data):
    """Analyze conjunction events data."""
    analysis = {
        'total_events': len(conjunction_data),
        'high_risk_events': len(conjunction_data[conjunction_data['probability'] > 0.01]),
        'avg_miss_distance': conjunction_data['miss_distance'].mean(),
        'avg_probability': conjunction_data['probability'].mean(),
        'recent_events': len(conjunction_data[conjunction_data['time_of_closest_approach'] > datetime.now() - timedelta(days=7)])
    }
    return analysis

def analyze_boxscore(boxscore_data):
    """Analyze boxscore data."""
    analysis = {
        'total_objects': boxscore_data['total_objects'].sum(),
        'active_satellites': boxscore_data['active_satellites'].sum(),
        'debris_objects': boxscore_data['debris'].sum(),
        'total_launches': boxscore_data['launches'].sum(),
        'countries': len(boxscore_data),
        'avg_objects_per_country': boxscore_data['total_objects'].mean()
    }
    return analysis
