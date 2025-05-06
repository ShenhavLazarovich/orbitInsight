import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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
        hovermode='closest'
    )
    
    return fig

def plot_3d_trajectory(df):
    """
    Plot 3D trajectory of satellite (X, Y, Z coordinates).
    
    Args:
        df: Pandas DataFrame with trajectory data
        
    Returns:
        Plotly figure object
    """
    # Check if necessary columns exist
    if not all(col in df.columns for col in ['x', 'y', 'z']):
        # Create empty figure with message if data is missing
        fig = go.Figure()
        fig.update_layout(
            title="Cannot create 3D trajectory plot: Missing X/Y/Z coordinate data",
            scene=dict(
                xaxis_title="X Position",
                yaxis_title="Y Position",
                zaxis_title="Z Position"
            )
        )
        return fig
    
    # Sort by timestamp if available
    if 'timestamp' in df.columns:
        df_sorted = df.sort_values('timestamp')
    else:
        df_sorted = df
    
    # Create 3D scatter plot
    fig = go.Figure(data=[
        go.Scatter3d(
            x=df_sorted['x'],
            y=df_sorted['y'],
            z=df_sorted['z'],
            mode='lines+markers',
            marker=dict(
                size=2,
                color=range(len(df_sorted)),
                colorscale='Viridis',
                opacity=0.8
            ),
            line=dict(
                color='darkblue',
                width=1
            ),
            name='Trajectory'
        )
    ])
    
    # Add start and end points
    fig.add_trace(
        go.Scatter3d(
            x=[df_sorted['x'].iloc[0]],
            y=[df_sorted['y'].iloc[0]],
            z=[df_sorted['z'].iloc[0]],
            mode='markers',
            marker=dict(size=5, color='green'),
            name='Start'
        )
    )
    
    fig.add_trace(
        go.Scatter3d(
            x=[df_sorted['x'].iloc[-1]],
            y=[df_sorted['y'].iloc[-1]],
            z=[df_sorted['z'].iloc[-1]],
            mode='markers',
            marker=dict(size=5, color='red'),
            name='End'
        )
    )
    
    # Add alert points if available
    if 'alert_type' in df.columns:
        alerts = df_sorted[df_sorted['alert_type'].notna()]
        if not alerts.empty:
            fig.add_trace(
                go.Scatter3d(
                    x=alerts['x'],
                    y=alerts['y'],
                    z=alerts['z'],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color='yellow',
                        symbol='diamond',
                        line=dict(color='black', width=1)
                    ),
                    name='Alerts'
                )
            )
    
    # Update layout
    fig.update_layout(
        title='3D Satellite Trajectory',
        scene=dict(
            xaxis_title='X Position (m)',
            yaxis_title='Y Position (m)',
            zaxis_title='Z Position (m)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30)
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
        hovermode='closest'
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
            # Calculate distance from origin (0,0,0)
            df['altitude'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
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
    
    # Add Earth radius reference if altitude is in appropriate range
    # Assuming altitude is in meters from Earth's surface
    if df['altitude'].median() > 100000:  # If altitude is likely in meters and in space
        fig.add_shape(
            type="line",
            x0=fig.data[0].x[0],
            y0=6371000,  # Earth radius in meters
            x1=fig.data[0].x[-1],
            y1=6371000,
            line=dict(
                color="Blue",
                width=1,
                dash="dash",
            ),
            name="Earth Radius"
        )
        
        fig.add_annotation(
            x=fig.data[0].x[0],
            y=6371000,
            text="Earth Radius (6371 km)",
            showarrow=False,
            yshift=10
        )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(title='Time'),
        yaxis=dict(title='Altitude (m)'),
        hovermode='closest'
    )
    
    return fig
