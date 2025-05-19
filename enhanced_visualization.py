import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
import plotly.graph_objects as go
from skyfield.api import load, EarthSatellite
from skyfield.positionlib import ICRF
from matplotlib.patches import Circle

def plot_ground_track(df, time_column='timestamp', lat_column='latitude', lon_column='longitude'):
    """
    Create a professional ground track visualization using Plotly with ONLY dots
    
    Args:
        df: DataFrame with satellite position data
        time_column: Name of the timestamp column
        lat_column: Name of the latitude column
        lon_column: Name of the longitude column
    
    Returns:
        Plotly figure object
    """
    # Create the base map
    fig = go.Figure()

    # Create the scatter trace with ONLY dots
    fig.add_trace(go.Scattergeo(
        lon=df[lon_column],
        lat=df[lat_column],
        mode='markers',  # ONLY markers, no lines possible
        hoverinfo='text',
        showlegend=True,
        name='Satellite Positions',
        marker=dict(
            size=4,
            color=np.arange(len(df)),
            colorscale=[
                [0, 'rgb(17,95,154)'],    # Deep blue for start
                [0.25, 'rgb(25,132,197)'], # Mid blue
                [0.5, 'rgb(114,172,211)'], # Light blue
                [0.75, 'rgb(182,214,227)'],# Very light blue
                [1, 'rgb(230,233,235)']    # Almost white for end
            ]
        ),
        hovertext=[f"<b>Position {i+1}</b><br>" +
                  f"Latitude: {lat:.3f}°<br>" +
                  f"Longitude: {lon:.3f}°<br>" +
                  (f"Time: {df[time_column].iloc[i]}" if time_column in df.columns else "")
                  for i, (lat, lon) in enumerate(zip(df[lat_column], df[lon_column]))]
    ))

    # Add start point
    fig.add_trace(go.Scattergeo(
        lon=[df[lon_column].iloc[0]],
        lat=[df[lat_column].iloc[0]],
        mode='markers',
        marker=dict(
            size=8,
            color='rgb(33,145,140)',
            symbol='diamond'
        ),
        name='Start Position',
        hovertext='Start Position<br>' +
                 f"Lat: {df[lat_column].iloc[0]:.3f}°<br>" +
                 f"Lon: {df[lon_column].iloc[0]:.3f}°"
    ))

    # Add end point
    fig.add_trace(go.Scattergeo(
        lon=[df[lon_column].iloc[-1]],
        lat=[df[lat_column].iloc[-1]],
        mode='markers',
        marker=dict(
            size=8,
            color='rgb(147,43,43)',
            symbol='diamond'
        ),
        name='End Position',
        hovertext='End Position<br>' +
                 f"Lat: {df[lat_column].iloc[-1]:.3f}°<br>" +
                 f"Lon: {df[lon_column].iloc[-1]:.3f}°"
    ))

    # Update map configuration
    fig.update_geos(
        projection_type="orthographic",
        showcoastlines=True,
        coastlinecolor="rgba(0, 0, 0, 0.5)",
        coastlinewidth=0.7,
        showland=True,
        landcolor="rgba(240, 240, 240, 0.8)",
        showocean=True,
        oceancolor="rgba(230, 240, 255, 0.8)",
        showlakes=True,
        lakecolor="rgba(230, 240, 255, 0.8)",
        showcountries=True,
        countrycolor="rgba(0, 0, 0, 0.2)",
        countrywidth=0.5,
        bgcolor='rgba(255, 255, 255, 0)',
        showframe=False,
        framecolor="rgba(0, 0, 0, 0.3)",
        framewidth=1,
        showgrid=True,
        gridcolor='rgba(0, 0, 0, 0.1)',
        gridwidth=0.5
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text='Satellite Position Points',
            font=dict(
                size=20,
                family='Arial, sans-serif',
                color='rgb(50, 50, 50)'
            ),
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        paper_bgcolor='rgba(255, 255, 255, 0.8)',
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0, 0, 0, 0.2)',
            borderwidth=1,
            font=dict(
                family='Arial, sans-serif',
                size=10,
                color='rgb(50, 50, 50)'
            )
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial, sans-serif'
        )
    )

    return fig

def calculate_ground_track(df):
    """
    Calculate ground track coordinates from satellite position data
    
    Args:
        df: DataFrame with x, y, z coordinates
        
    Returns:
        DataFrame with added latitude and longitude columns
    """
    # Convert ECEF coordinates to lat/lon
    lats = []
    lons = []
    
    for _, row in df.iterrows():
        try:
            # Convert coordinates from meters to kilometers
            x, y, z = row['x']/1000, row['y']/1000, row['z']/1000
            
            # Calculate lat/lon using spherical coordinates
            r = np.sqrt(x*x + y*y + z*z)
            lat = np.arcsin(z/r) * 180/np.pi
            lon = np.arctan2(y, x) * 180/np.pi
            
            lats.append(lat)
            lons.append(lon)
            
        except Exception as e:
            print(f"Error converting coordinates: {e}")
            lats.append(0)
            lons.append(0)
    
    # Add to dataframe
    df['latitude'] = lats
    df['longitude'] = lons
    
    return df

def plot_static_ground_track(df, save_path=None):
    """
    Create a static ground track visualization using Cartopy
    
    Args:
        df: DataFrame with latitude and longitude columns
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib figure object
    """
    # Create figure with projection
    fig = plt.figure(figsize=(15, 10))
    ax = plt.axes(projection=ccrs.Robinson())
    
    # Add map features
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines()
    
    # Plot ground track
    plt.plot(df['longitude'], df['latitude'],
             color='blue', linewidth=0, transform=ccrs.Geodetic(),
             label='Ground Track')
    
    # Add start and end points
    plt.plot(df['longitude'].iloc[0], df['latitude'].iloc[0],
             'go', markersize=10, transform=ccrs.Geodetic(),
             label='Start')
    plt.plot(df['longitude'].iloc[-1], df['latitude'].iloc[-1],
             'ro', markersize=10, transform=ccrs.Geodetic(),
             label='End')
    
    # Add title and legend
    plt.title('Satellite Ground Track', pad=20)
    plt.legend(loc='upper right')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    return fig 

def plot_3d_enhanced(df, time_column='timestamp'):
    """
    Create an enhanced 3D visualization with better Earth model and lighting
    
    Args:
        df: DataFrame with satellite position data (in meters)
        time_column: Name of the timestamp column
    
    Returns:
        Plotly figure object
    """
    # Create the figure
    fig = go.Figure()
    
    # Earth radius in meters (convert to km for better scaling)
    r_earth = 6371  # km
    
    # Convert trajectory coordinates to kilometers for better scaling
    df_scaled = df.copy()
    df_scaled[['x', 'y', 'z']] = df[['x', 'y', 'z']] / 1000  # Convert to km
    
    # Create Earth sphere points with higher resolution
    phi = np.linspace(0, 2*np.pi, 180)  # Increased resolution
    theta = np.linspace(-np.pi/2, np.pi/2, 180)  # Increased resolution
    phi, theta = np.meshgrid(phi, theta)
    
    # Create Earth sphere coordinates
    x_earth = r_earth * np.cos(theta) * np.cos(phi)
    y_earth = r_earth * np.cos(theta) * np.sin(phi)
    z_earth = r_earth * np.sin(theta)
    
    # Add Earth as a surface with improved appearance
    fig.add_trace(go.Surface(
        x=x_earth,
        y=y_earth,
        z=z_earth,
        colorscale=[
            [0, 'rgb(0,0,80)'],      # Deep ocean
            [0.2, 'rgb(0,50,150)'],   # Ocean
            [0.4, 'rgb(0,100,200)'],  # Shallow ocean
            [0.5, 'rgb(30,150,30)'],  # Lowlands
            [0.6, 'rgb(100,170,30)'], # Plains
            [0.7, 'rgb(160,150,50)'], # Highlands
            [0.8, 'rgb(200,200,200)'] # Mountains
        ],
        showscale=False,
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            fresnel=0.2,
            specular=0.5,
            roughness=0.5
        ),
        opacity=0.9,
        name='Earth'
    ))
    
    # Add trajectory with improved visibility
    # Main trajectory line
    fig.add_trace(go.Scatter3d(
        x=df_scaled['x'],
        y=df_scaled['y'],
        z=df_scaled['z'],
        mode='lines',
        line=dict(
            color=np.arange(len(df)),
            colorscale='Viridis',
            width=5
        ),
        name='Trajectory'
    ))
    
    # Add points with time-based coloring
    fig.add_trace(go.Scatter3d(
        x=df_scaled['x'],
        y=df_scaled['y'],
        z=df_scaled['z'],
        mode='markers',
        marker=dict(
            size=3,
            color=np.arange(len(df)),
            colorscale='Viridis',
            opacity=0.8,
            showscale=True,
            colorbar=dict(
                title='Time Sequence',
                thickness=15,
                len=0.6,
                tickmode='auto',
                nticks=10
            )
        ),
        name='Position Points'
    ))
    
    # Add start and end points with improved visibility
    fig.add_trace(go.Scatter3d(
        x=[df_scaled['x'].iloc[0]],
        y=[df_scaled['y'].iloc[0]],
        z=[df_scaled['z'].iloc[0]],
        mode='markers',
        marker=dict(
            size=8,
            color='green',
            symbol='diamond',
            line=dict(color='white', width=1)
        ),
        name='Start'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[df_scaled['x'].iloc[-1]],
        y=[df_scaled['y'].iloc[-1]],
        z=[df_scaled['z'].iloc[-1]],
        mode='markers',
        marker=dict(
            size=8,
            color='red',
            symbol='diamond',
            line=dict(color='white', width=1)
        ),
        name='End'
    ))
    
    # Calculate appropriate camera distance based on trajectory
    max_coord = max(abs(df_scaled[['x', 'y', 'z']].values.flatten()))
    camera_distance = max(max_coord * 2, r_earth * 2)
    
    # Add reference axes for scale
    axis_length = r_earth * 1.5
    # X-axis (red)
    fig.add_trace(go.Scatter3d(
        x=[0, axis_length], y=[0, 0], z=[0, 0],
        mode='lines',
        line=dict(color='red', width=2),
        name='X-axis'
    ))
    # Y-axis (green)
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, axis_length], z=[0, 0],
        mode='lines',
        line=dict(color='green', width=2),
        name='Y-axis'
    ))
    # Z-axis (blue)
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[0, axis_length],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Z-axis'
    ))
    
    # Update layout for better visualization
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=camera_distance*0.7, y=camera_distance*0.7, z=camera_distance*0.4)
            ),
            xaxis=dict(
                title='X (km)',
                showbackground=True,
                backgroundcolor='rgba(230, 230,230,0.1)',
                gridcolor='white',
                showgrid=True,
                zeroline=True,
                zerolinecolor='white'
            ),
            yaxis=dict(
                title='Y (km)',
                showbackground=True,
                backgroundcolor='rgba(230, 230,230,0.1)',
                gridcolor='white',
                showgrid=True,
                zeroline=True,
                zerolinecolor='white'
            ),
            zaxis=dict(
                title='Z (km)',
                showbackground=True,
                backgroundcolor='rgba(230, 230,230,0.1)',
                gridcolor='white',
                showgrid=True,
                zeroline=True,
                zerolinecolor='white'
            )
        ),
        title=dict(
            text='Enhanced 3D Satellite Trajectory',
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=20)
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.1)'
        ),
        height=800
    )
    
    # Calculate and add altitude information
    altitudes = np.sqrt(df_scaled['x']**2 + df_scaled['y']**2 + df_scaled['z']**2) - r_earth
    min_alt = altitudes.min()
    max_alt = altitudes.max()
    avg_alt = altitudes.mean()
    
    # Add altitude information with improved formatting
    fig.add_annotation(
        text=(f"<b>Altitude Information</b><br>" +
              f"Range: {min_alt:.1f} - {max_alt:.1f} km<br>" +
              f"Average: {avg_alt:.1f} km"),
        xref="paper", yref="paper",
        x=0, y=1.05,
        showarrow=False,
        font=dict(size=14),
        bgcolor='rgba(255, 255, 255, 0.1)',
        bordercolor='rgba(255, 255, 255, 0.2)',
        borderwidth=1,
        borderpad=4
    )
    
    return fig

def plot_orbital_parameters(df):
    """
    Create visualizations for orbital parameters analysis
    
    Args:
        df: DataFrame with satellite position and velocity data
        
    Returns:
        Dictionary of Plotly figure objects
    """
    figs = {}
    
    # Calculate orbital parameters
    r = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
    v = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
    
    # Altitude vs Time
    fig_alt = go.Figure()
    fig_alt.add_trace(go.Scatter(
        x=df['timestamp'],
        y=r - 6371000,  # Convert to altitude above Earth's surface
        mode='lines',
        name='Altitude'
    ))
    fig_alt.update_layout(
        title='Altitude vs Time',
        xaxis_title='Time',
        yaxis_title='Altitude (m)',
        height=400
    )
    figs['altitude'] = fig_alt
    
    # Velocity vs Time
    fig_vel = go.Figure()
    fig_vel.add_trace(go.Scatter(
        x=df['timestamp'],
        y=v,
        mode='lines',
        name='Velocity'
    ))
    fig_vel.update_layout(
        title='Velocity vs Time',
        xaxis_title='Time',
        yaxis_title='Velocity (m/s)',
        height=400
    )
    figs['velocity'] = fig_vel
    
    return figs 

def create_3d_orbit_visualization(df):
    """
    Create an interactive 3D orbital visualization with Earth reference
    
    Args:
        df: DataFrame with satellite position data (x, y, z coordinates in meters)
        
    Returns:
        Plotly figure object
    """
    # Create the figure
    fig = go.Figure()
    
    # Convert coordinates to kilometers for better scaling
    scale_factor = 1000  # convert meters to kilometers
    x = df['x'] / scale_factor
    y = df['y'] / scale_factor
    z = df['z'] / scale_factor
    
    # Create the satellite trajectory
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        name='Satellite Trajectory',
        marker=dict(
            size=2,
            color=np.arange(len(df)),
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
        hoverinfo='text',
        text=[f"Point {i+1}<br>X: {x_:.2f} km<br>Y: {y_:.2f} km<br>Z: {z_:.2f} km" 
              for i, (x_, y_, z_) in enumerate(zip(x, y, z))]
    ))
    
    # Add start and end points
    fig.add_trace(go.Scatter3d(
        x=[x.iloc[0]], y=[y.iloc[0]], z=[z.iloc[0]],
        mode='markers',
        name='Start',
        marker=dict(size=5, color='green')
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[x.iloc[-1]], y=[y.iloc[-1]], z=[z.iloc[-1]],
        mode='markers',
        name='End',
        marker=dict(size=5, color='red')
    ))
    
    # Create Earth sphere
    earth_radius = 6371  # Earth radius in kilometers
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 50)
    earth_x = earth_radius * np.outer(np.cos(u), np.sin(v))
    earth_y = earth_radius * np.outer(np.sin(u), np.sin(v))
    earth_z = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Add semi-transparent Earth
    fig.add_surface(
        x=earth_x,
        y=earth_y,
        z=earth_z,
        colorscale=[[0, 'rgb(0,0,255)'], [1, 'rgb(100,100,255)']],
        opacity=0.3,
        showscale=False,
        name='Earth'
    )
    
    # Calculate appropriate camera position
    max_range = np.max([
        np.ptp(x),
        np.ptp(y),
        np.ptp(z)
    ]) / 2
    
    mid_x = np.mean([np.min(x), np.max(x)])
    mid_y = np.mean([np.min(y), np.max(y)])
    mid_z = np.mean([np.min(z), np.max(z)])
    
    # Update layout with improved camera and scene settings
    fig.update_layout(
        scene=dict(
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            aspectmode='data',
            xaxis=dict(title='X (km)'),
            yaxis=dict(title='Y (km)'),
            zaxis=dict(title='Z (km)'),
            annotations=[
                dict(x=earth_radius*1.1, y=0, z=0, text="X"),
                dict(x=0, y=earth_radius*1.1, z=0, text="Y"),
                dict(x=0, y=0, z=earth_radius*1.1, text="Z")
            ]
        ),
        title=dict(
            text='3D Orbital Visualization',
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=700,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig 