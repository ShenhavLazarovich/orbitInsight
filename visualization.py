import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import folium
from datetime import datetime, timedelta

def plot_2d_trajectory(df):
    """
    Plot 2D trajectory of satellite (X vs Y coordinates).
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        Plotly figure object
    """
    # Check if necessary columns exist
    if not all(col in df.columns for col in ['x', 'y']):
        # Create empty figure with message if data is missing
        fig = go.Figure()
        fig.update_layout(
            title="Cannot create 2D trajectory plot: Missing X/Y coordinate data",
            xaxis_title="X Position",
            yaxis_title="Y Position"
        )
        return fig
    
    # Create scatter plot of trajectory
    fig = px.scatter(
        df, 
        x='x', 
        y='y',
        title="2D Satellite Trajectory",
        labels={'x': 'X Position (m)', 'y': 'Y Position (m)'}
    )
    
    # Add line connecting points in chronological order
    if 'timestamp' in df.columns:
        df_sorted = df.sort_values('timestamp')
    else:
        df_sorted = df
        
    fig.add_trace(
        go.Scatter(
            x=df_sorted['x'],
            y=df_sorted['y'],
            mode='lines',
            name='Path',
            line=dict(width=1, color='rgba(0,0,0,0.5)')
        )
    )
    
    # Highlight start and end points
    fig.add_trace(
        go.Scatter(
            x=[df_sorted['x'].iloc[0]],
            y=[df_sorted['y'].iloc[0]],
            mode='markers',
            name='Start',
            marker=dict(size=10, color='green')
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=[df_sorted['x'].iloc[-1]],
            y=[df_sorted['y'].iloc[-1]],
            mode='markers',
            name='End',
            marker=dict(size=10, color='red')
        )
    )
    
    # Improve layout
    fig.update_layout(
        xaxis=dict(showgrid=True, zeroline=True),
        yaxis=dict(showgrid=True, zeroline=True),
        hovermode='closest',
        height=600  # Increase the plot height
    )
    
    return fig

def plot_3d_trajectory(satellite_data):
    """Create a 3D plot of satellite trajectory."""
    fig = go.Figure()
    
    # Add Earth sphere
    earth_radius = 6371  # km
    phi = np.linspace(0, 2*np.pi, 100)
    theta = np.linspace(-np.pi/2, np.pi/2, 100)
    phi, theta = np.meshgrid(phi, theta)
    
    x = earth_radius * np.cos(theta) * np.cos(phi)
    y = earth_radius * np.cos(theta) * np.sin(phi)
    z = earth_radius * np.sin(theta)
    
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        opacity=0.3,
        showscale=False,
        colorscale='Blues'
    ))
    
    # Add satellite trajectory
    for _, sat in satellite_data.iterrows():
        # Calculate trajectory points
        t = np.linspace(0, 2*np.pi, 100)
        a = sat['SEMIMAJOR_AXIS']  # km
        e = sat['ECCENTRICITY']
        i = np.radians(sat['INCLINATION'])
        raan = np.radians(sat['RA_OF_ASC_NODE'])
        w = np.radians(sat['ARG_OF_PERICENTER'])
        
        # Calculate position
        r = a * (1 - e**2) / (1 + e * np.cos(t))
        x = r * (np.cos(raan) * np.cos(w + t) - np.sin(raan) * np.sin(w + t) * np.cos(i))
        y = r * (np.sin(raan) * np.cos(w + t) + np.cos(raan) * np.sin(w + t) * np.cos(i))
        z = r * np.sin(w + t) * np.sin(i)
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            name=sat['OBJECT_NAME'],
            line=dict(width=2)
        ))
    
    # Update layout
    fig.update_layout(
        title='Satellite Trajectory',
        scene=dict(
            aspectmode='data',
            xaxis_title='X (km)',
            yaxis_title='Y (km)',
            zaxis_title='Z (km)'
        ),
        showlegend=True
    )
    
    return fig

def plot_time_series(df, parameter):
    """
    Plot time series of a specific parameter.
    
    Args:
        df: Pandas DataFrame with trajectory data
        parameter: Column name to plot over time
        
    Returns:
        Plotly figure object
    """
    # Check if parameter exists in the dataframe
    if parameter not in df.columns:
        # Create empty figure with message if parameter doesn't exist
        fig = go.Figure()
        fig.update_layout(
            title=f"Parameter '{parameter}' not found in data",
            xaxis_title="Time",
            yaxis_title="Value"
        )
        return fig
    
    # Check if timestamp column exists
    if 'timestamp' not in df.columns:
        # Use index as X-axis if timestamp doesn't exist
        fig = px.line(
            df, 
            x=df.index, 
            y=parameter,
            title=f"Time Series of {parameter}",
            labels={'x': 'Index', 'y': parameter}
        )
    else:
        # Sort by timestamp
        df_sorted = df.sort_values('timestamp')
        
        # Create line plot
        fig = px.line(
            df_sorted, 
            x='timestamp', 
            y=parameter,
            title=f"Time Series of {parameter}",
            labels={'timestamp': 'Time', parameter: parameter}
        )
    
    # Add markers for alerts if they exist
    if 'alert_type' in df.columns:
        alerts = df[df['alert_type'].notna()]
        if not alerts.empty:
            if 'timestamp' in df.columns:
                x_values = alerts['timestamp']
            else:
                x_values = alerts.index
                
            fig.add_trace(
                go.Scatter(
                    x=x_values,
                    y=alerts[parameter],
                    mode='markers',
                    name='Alerts',
                    marker=dict(
                        size=10,
                        color='red',
                        symbol='triangle-up'
                    )
                )
            )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title='Time'),
        yaxis=dict(title=parameter),
        hovermode='closest',
        height=600  # Increase the plot height
    )
    
    return fig

def plot_altitude_profile(df):
    """
    Plot altitude profile of the satellite.
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        Plotly figure object
    """
    # Check if altitude column exists
    if 'altitude' not in df.columns:
        # Try to calculate altitude from x, y, z coordinates
        if all(col in df.columns for col in ['x', 'y', 'z']):
            # Calculate distance from Earth center (0,0,0) and subtract Earth radius
            # Earth radius is approximately 6371 km or 6371000 meters
            earth_radius = 6371000  # in meters
            
            # Calculate distance from Earth center
            distance_from_center = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
            
            # Subtract Earth radius to get altitude
            df['altitude'] = distance_from_center - earth_radius
            
            # If altitude is negative (shouldn't normally happen), set to a small positive value
            df.loc[df['altitude'] < 0, 'altitude'] = 0
            
            print(f"Calculated altitudes range from {df['altitude'].min():.2f} to {df['altitude'].max():.2f} meters")
        else:
            # Create empty figure with message if altitude data is missing
            fig = go.Figure()
            fig.update_layout(
                title="Cannot create altitude profile: Missing altitude data",
                xaxis_title="Time",
                yaxis_title="Altitude"
            )
            return fig
    
    # Check if timestamp column exists
    if 'timestamp' not in df.columns:
        # Use index as X-axis if timestamp doesn't exist
        fig = px.line(
            df, 
            x=df.index, 
            y='altitude',
            title="Satellite Altitude Profile",
            labels={'index': 'Data Point', 'altitude': 'Altitude (m)'}
        )
    else:
        # Sort by timestamp
        df_sorted = df.sort_values('timestamp')
        
        # Create line plot
        fig = px.line(
            df_sorted, 
            x='timestamp', 
            y='altitude',
            title="Satellite Altitude Profile",
            labels={'timestamp': 'Time', 'altitude': 'Altitude (m)'}
        )
    
    # Add a smoother trend line
    if len(df) > 5:  # Only add trend line if we have enough points
        if 'timestamp' in df.columns:
            df_sorted = df.sort_values('timestamp')
            x_values = df_sorted['timestamp']
        else:
            df_sorted = df
            x_values = df_sorted.index
            
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df_sorted['altitude'].rolling(window=5, min_periods=1).mean(),
                mode='lines',
                name='Moving Average (5)',
                line=dict(color='rgba(255, 0, 0, 0.7)', width=2)
            )
        )
    
    # Calculate appropriate y-axis range based on data
    min_alt = df['altitude'].min()
    max_alt = df['altitude'].max()
    
    # Determine if we should display in km instead of meters for better readability
    use_km = max_alt > 100000  # Use km if altitude exceeds 100km
    
    # Convert to km if needed
    if use_km:
        min_alt_display = min_alt / 1000
        max_alt_display = max_alt / 1000
        y_axis_title = 'Altitude (km)'
        earth_radius_display = 6371  # Earth radius in km
    else:
        min_alt_display = min_alt
        max_alt_display = max_alt
        y_axis_title = 'Altitude (m)'
        earth_radius_display = 6371000  # Earth radius in m
    
    # Add Earth radius reference if altitude is in appropriate range
    if df['altitude'].median() > 100000:  # If altitude is likely in meters and in space
        fig.add_shape(
            type="line",
            x0=fig.data[0].x[0],
            y0=earth_radius_display,  # Now uses the appropriate units
            x1=fig.data[0].x[-1],
            y1=earth_radius_display,
            line=dict(
                color="Blue",
                width=1,
                dash="dash",
            ),
            name="Earth Radius"
        )
        
        fig.add_annotation(
            x=fig.data[0].x[0],
            y=earth_radius_display,
            text=f"Earth Radius ({earth_radius_display:,} {'km' if use_km else 'm'})",
            showarrow=False,
            yshift=10
        )
    
    # Add buffer for y-axis range (10% of data range)
    y_range_buffer = (max_alt_display - min_alt_display) * 0.1
    
    # Ensure we don't have a zero or negative range
    if max_alt_display - min_alt_display < (10 if use_km else 100):
        y_range_buffer = 10 if use_km else 100  # Set minimum range
    
    # Update layout with properly scaled y-axis
    fig.update_layout(
        xaxis=dict(title='Time'),
        yaxis=dict(
            title=y_axis_title,
            range=[max(0, min_alt_display - y_range_buffer), max_alt_display + y_range_buffer],  # Ensure never below 0
            autorange=False  # Disable autorange to use our custom range
        ),
        hovermode='closest'
    )
    
    # Update Earth radius reference to use correct units if it exists
    if hasattr(fig.layout, 'shapes') and fig.layout.shapes:
        for shape in fig.layout.shapes:
            if hasattr(shape, 'line') and hasattr(shape.line, 'dash') and shape.line.dash == 'dash':
                shape.y0 = earth_radius_display
                shape.y1 = earth_radius_display
                
    # Update Earth radius annotation if it exists
    if hasattr(fig.layout, 'annotations') and fig.layout.annotations:
        for annotation in fig.layout.annotations:
            if 'Earth Radius' in annotation.text:
                annotation.y = earth_radius_display
                annotation.text = f"Earth Radius ({earth_radius_display:,} {'km' if use_km else 'm'})"
    
    return fig

<<<<<<< Updated upstream
def plot_launch_timeline(catalog_data):
    """Create a launch timeline plot."""
    fig = px.histogram(
        catalog_data,
        x='launch_date',
        title='Satellite Launch Timeline',
        labels={'launch_date': 'Launch Date', 'count': 'Number of Satellites'}
    )
    return fig

def plot_country_distribution(catalog_data):
    """Create a country distribution plot."""
    fig = px.pie(
        catalog_data,
        names='country',
        title='Satellite Distribution by Country'
    )
    return fig

def plot_status_distribution(catalog_data):
    """Create a status distribution plot."""
    fig = px.pie(
        catalog_data,
        names='status',
        title='Satellite Status Distribution'
    )
    return fig

def plot_launch_sites_map(launch_sites_data):
    """Create a world map of launch sites."""
    fig = px.scatter_geo(
        launch_sites_data,
        lat='latitude',
        lon='longitude',
        hover_name='name',
        hover_data=['country', 'status', 'launch_count'],
        title='Launch Sites World Map'
    )
    return fig

def plot_launch_activity(launch_sites_data):
    """Create a launch activity plot."""
    fig = px.line(
        launch_sites_data,
        x='last_launch',
        y='launch_count',
        color='name',
        title='Launch Activity by Site',
        labels={'last_launch': 'Date', 'launch_count': 'Number of Launches'}
    )
    return fig

def plot_launch_sites_by_country(launch_sites_data):
    """Create a country distribution plot for launch sites."""
    fig = px.bar(
        launch_sites_data.groupby('country')['launch_count'].sum().reset_index(),
        x='country',
        y='launch_count',
        title='Launch Activity by Country',
        labels={'country': 'Country', 'launch_count': 'Total Launches'}
    )
    return fig

def plot_decay_timeline(decay_data):
    """Create a decay timeline plot."""
    fig = px.histogram(
        decay_data,
        x='decay_date',
        title='Satellite Decay Timeline',
        labels={'decay_date': 'Decay Date', 'count': 'Number of Decays'}
    )
    return fig

def plot_decay_altitude_distribution(decay_data):
    """Create an altitude distribution plot for decay events."""
    fig = px.histogram(
        decay_data,
        x='pre_decay_altitude',
        title='Pre-Decay Altitude Distribution',
        labels={'pre_decay_altitude': 'Altitude (km)', 'count': 'Number of Decays'}
    )
    return fig

def plot_decay_by_country(decay_data):
    """Create a country distribution plot for decay events."""
    fig = px.pie(
        decay_data,
        names='country',
        title='Decay Events by Country'
    )
    return fig

def plot_conjunction_timeline(conjunction_data):
    """Create a conjunction timeline plot."""
    fig = px.histogram(
        conjunction_data,
        x='time_of_closest_approach',
        title='Conjunction Events Timeline',
        labels={'time_of_closest_approach': 'Time', 'count': 'Number of Events'}
    )
    return fig

def plot_conjunction_risk_distribution(conjunction_data):
    """Create a risk distribution plot for conjunction events."""
    fig = px.histogram(
        conjunction_data,
        x='probability',
        title='Conjunction Risk Distribution',
        labels={'probability': 'Collision Probability', 'count': 'Number of Events'}
    )
    return fig

def plot_conjunction_distance_analysis(conjunction_data):
    """Create a miss distance analysis plot."""
    fig = px.scatter(
        conjunction_data,
        x='miss_distance',
        y='probability',
        title='Miss Distance vs. Collision Probability',
        labels={'miss_distance': 'Miss Distance (km)', 'probability': 'Collision Probability'}
    )
    return fig

def plot_object_distribution(boxscore_data):
    """Create an object distribution plot."""
    fig = px.bar(
        boxscore_data,
        x='country',
        y=['active_satellites', 'debris', 'payloads', 'rocket_bodies'],
        title='Space Object Distribution by Country',
        labels={'value': 'Number of Objects', 'variable': 'Object Type'}
    )
    return fig

def plot_launch_activity_by_country(boxscore_data):
    """Create a launch activity plot by country."""
    fig = px.bar(
        boxscore_data,
        x='country',
        y='launches',
        title='Launch Activity by Country',
        labels={'launches': 'Number of Launches'}
    )
    return fig

def plot_debris_analysis(boxscore_data):
    """Create a debris analysis plot."""
    fig = px.pie(
        boxscore_data,
        values='debris',
        names='country',
        title='Debris Distribution by Country'
    )
=======
def plot_ground_track(df):
    """
    Plot satellite ground track on a world map.
    
    Args:
        df: Pandas DataFrame with trajectory data containing latitude and longitude
        
    Returns:
        Plotly figure object
    """
    # Convert cartesian coordinates to lat/lon if needed
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        if all(col in df.columns for col in ['x', 'y', 'z']):
            # Convert XYZ to lat/lon
            r = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
            df['latitude'] = np.arcsin(df['z'] / r) * 180 / np.pi
            df['longitude'] = np.arctan2(df['y'], df['x']) * 180 / np.pi
        else:
            # Create empty figure with message if data is missing
            fig = go.Figure()
            fig.update_layout(
                title="Cannot create ground track plot: Missing coordinate data",
                mapbox=dict(style="open-street-map"),
            )
            return fig
    
    # Sort by timestamp if available
    if 'timestamp' in df.columns:
        df_sorted = df.sort_values('timestamp')
    else:
        df_sorted = df
    
    # Create the ground track plot
    fig = go.Figure()
    
    # Add the ground track line
    fig.add_trace(
        go.Scattermapbox(
            lat=df_sorted['latitude'],
            lon=df_sorted['longitude'],
            mode='lines+markers',
            marker=dict(
                size=4,
                color=list(range(len(df_sorted))),
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(
                    title="Time Sequence",
                    thickness=20
                )
            ),
            line=dict(
                color='darkblue',
                width=2
            ),
            name='Ground Track'
        )
    )
    
    # Add start and end points
    fig.add_trace(
        go.Scattermapbox(
            lat=[df_sorted['latitude'].iloc[0]],
            lon=[df_sorted['longitude'].iloc[0]],
            mode='markers',
            marker=dict(size=10, color='green'),
            name='Start'
        )
    )
    
    fig.add_trace(
        go.Scattermapbox(
            lat=[df_sorted['latitude'].iloc[-1]],
            lon=[df_sorted['longitude'].iloc[-1]],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='End'
        )
    )
    
    # Update layout with map configuration
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(
                lat=df_sorted['latitude'].mean(),
                lon=df_sorted['longitude'].mean()
            ),
            zoom=1
        ),
        showlegend=True,
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
>>>>>>> Stashed changes
    return fig

def plot_2d_trajectory(satellite_data):
    """Create a 2D map of satellite trajectory."""
    # Create base map
    m = folium.Map()
    
    for _, sat in satellite_data.iterrows():
        # Calculate ground track points
        t = np.linspace(0, 2*np.pi, 100)
        a = sat['SEMIMAJOR_AXIS']  # km
        e = sat['ECCENTRICITY']
        i = np.radians(sat['INCLINATION'])
        raan = np.radians(sat['RA_OF_ASC_NODE'])
        w = np.radians(sat['ARG_OF_PERICENTER'])
        
        # Calculate position
        r = a * (1 - e**2) / (1 + e * np.cos(t))
        x = r * (np.cos(raan) * np.cos(w + t) - np.sin(raan) * np.sin(w + t) * np.cos(i))
        y = r * (np.sin(raan) * np.cos(w + t) + np.cos(raan) * np.sin(w + t) * np.cos(i))
        z = r * np.sin(w + t) * np.sin(i)
        
        # Convert to lat/lon
        lat = np.degrees(np.arcsin(z / r))
        lon = np.degrees(np.arctan2(y, x))
        
        # Create ground track line
        points = list(zip(lat, lon))
        folium.PolyLine(
            points,
            color='red',
            weight=2,
            opacity=0.8,
            popup=sat['OBJECT_NAME']
        ).add_to(m)
        
        # Add marker at current position
        folium.Marker(
            [lat[0], lon[0]],
            popup=f"{sat['OBJECT_NAME']}<br>NORAD ID: {sat['NORAD_ID']}",
            tooltip=sat['OBJECT_NAME']
        ).add_to(m)
    
    return m

def plot_altitude_distribution(satellite_data):
    """Create a histogram of satellite altitudes."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=satellite_data['APOGEE'],
        name='Apogee',
        opacity=0.7
    ))
    
    fig.add_trace(go.Histogram(
        x=satellite_data['PERIGEE'],
        name='Perigee',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Satellite Altitude Distribution',
        xaxis_title='Altitude (km)',
        yaxis_title='Number of Satellites',
        barmode='overlay'
    )
    
    return fig

def plot_conjunction_risk(satellite_data):
    """Create a scatter plot of conjunction risk."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=satellite_data['TCA'],
        y=satellite_data['MISS_DISTANCE'],
        mode='markers',
        marker=dict(
            size=10,
            color=satellite_data['RISK_LEVEL'].map({
                'HIGH': 'red',
                'MEDIUM': 'orange',
                'LOW': 'green'
            }),
            opacity=0.7
        ),
        text=satellite_data['OBJECT_NAME'],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Conjunction Risk Analysis',
        xaxis_title='Time of Closest Approach',
        yaxis_title='Miss Distance (km)',
        showlegend=False
    )
    
    return fig

def plot_launch_statistics(launch_data):
    """Create a bar chart of launch statistics."""
    fig = go.Figure()
    
    # Group by launch site
    site_stats = launch_data.groupby('SITE_NAME').size().reset_index(name='count')
    
    fig.add_trace(go.Bar(
        x=site_stats['SITE_NAME'],
        y=site_stats['count'],
        text=site_stats['count'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Launch Statistics by Site',
        xaxis_title='Launch Site',
        yaxis_title='Number of Launches',
        xaxis_tickangle=-45
    )
    
    return fig
