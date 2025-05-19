import pandas as pd
import io
from datetime import datetime
import numpy as np

def generate_satellite_report(trajectory_data, tle_data, stats, track_data=None, format='excel'):
    """
    Generate a comprehensive satellite report in the specified format.
    
    Args:
        trajectory_data: DataFrame with trajectory information
        tle_data: DataFrame with TLE information
        stats: Dictionary containing orbital statistics
        track_data: Optional DataFrame with ground track data
        format: Output format ('excel' or 'csv')
    
    Returns:
        Bytes object containing the report data
    """
    # Create a BytesIO object to store the report
    output = io.BytesIO()
    
    if format == 'excel':
        # Create Excel writer object
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Satellite Information Sheet
            satellite_info = {
                'Parameter': [
                    'Satellite ID',
                    'Name',
                    'Launch Date',
                    'Object Type',
                    'Country of Origin',
                    'TLE Epoch',
                    'TLE Line 1',
                    'TLE Line 2'
                ],
                'Value': [
                    tle_data['NORAD_CAT_ID'].iloc[0] if not tle_data.empty else 'N/A',
                    tle_data['OBJECT_NAME'].iloc[0] if not tle_data.empty else 'N/A',
                    tle_data['LAUNCH_DATE'].iloc[0] if not tle_data.empty and 'LAUNCH_DATE' in tle_data.columns else 'N/A',
                    tle_data['OBJECT_TYPE'].iloc[0] if not tle_data.empty and 'OBJECT_TYPE' in tle_data.columns else 'N/A',
                    tle_data['COUNTRY_CODE'].iloc[0] if not tle_data.empty and 'COUNTRY_CODE' in tle_data.columns else 'N/A',
                    tle_data['EPOCH'].iloc[0] if not tle_data.empty else 'N/A',
                    tle_data['TLE_LINE1'].iloc[0] if not tle_data.empty else 'N/A',
                    tle_data['TLE_LINE2'].iloc[0] if not tle_data.empty else 'N/A'
                ]
            }
            pd.DataFrame(satellite_info).to_excel(writer, sheet_name='Satellite Info', index=False)
            
            # Orbital Parameters Sheet
            orbital_params = {
                'Parameter': [
                    'Average Altitude',
                    'Maximum Altitude',
                    'Minimum Altitude',
                    'Orbit Period',
                    'Maximum Velocity',
                    'Inclination',
                    'Eccentricity',
                    'Mean Motion'
                ],
                'Value': [
                    f"{stats.get('avg_altitude', 'N/A')} km",
                    f"{stats.get('max_altitude', 'N/A')} km",
                    f"{stats.get('min_altitude', 'N/A')} km",
                    f"{stats.get('orbit_period', 'N/A')} min",
                    f"{stats.get('max_velocity', 'N/A')} km/s",
                    f"{tle_data['INCLINATION'].iloc[0] if not tle_data.empty and 'INCLINATION' in tle_data.columns else 'N/A'} deg",
                    tle_data['ECCENTRICITY'].iloc[0] if not tle_data.empty and 'ECCENTRICITY' in tle_data.columns else 'N/A',
                    f"{tle_data['MEAN_MOTION'].iloc[0] if not tle_data.empty and 'MEAN_MOTION' in tle_data.columns else 'N/A'} rev/day"
                ]
            }
            pd.DataFrame(orbital_params).to_excel(writer, sheet_name='Orbital Parameters', index=False)
            
            # Trajectory Data Sheet
            if not trajectory_data.empty:
                # Convert timestamps to datetime if they're not already
                if 'timestamp' in trajectory_data.columns:
                    trajectory_data['timestamp'] = pd.to_datetime(trajectory_data['timestamp'])
                
                # Format trajectory data
                trajectory_export = trajectory_data.copy()
                # Convert coordinates to km for better readability
                for col in ['x', 'y', 'z']:
                    if col in trajectory_export.columns:
                        trajectory_export[f'{col}_km'] = trajectory_export[col] / 1000
                        trajectory_export.drop(col, axis=1, inplace=True)
                
                trajectory_export.to_excel(writer, sheet_name='Trajectory Data', index=False)
            
            # Ground Track Sheet
            if track_data is not None and not track_data.empty:
                track_data.to_excel(writer, sheet_name='Ground Track', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#D9E1F2',
                'border': 1
            })
            
            # Apply formatting to all sheets
            for worksheet in writer.sheets.values():
                worksheet.set_row(0, None, header_format)
                worksheet.autofit()
    
    elif format == 'csv':
        # For CSV, we'll just include the main trajectory data
        if not trajectory_data.empty:
            trajectory_export = trajectory_data.copy()
            # Convert coordinates to km
            for col in ['x', 'y', 'z']:
                if col in trajectory_export.columns:
                    trajectory_export[f'{col}_km'] = trajectory_export[col] / 1000
                    trajectory_export.drop(col, axis=1, inplace=True)
            
            output.write(trajectory_export.to_csv(index=False).encode('utf-8'))
    
    # Reset buffer position
    output.seek(0)
    
    return output

def generate_analysis_report(trajectory_data, analysis_results, format='excel'):
    """
    Generate a detailed analysis report including statistical measures and derived metrics.
    
    Args:
        trajectory_data: DataFrame with trajectory information
        analysis_results: Dictionary containing analysis results
        format: Output format ('excel' or 'csv')
    
    Returns:
        Bytes object containing the report data
    """
    output = io.BytesIO()
    
    if format == 'excel':
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Basic Statistics Sheet
            if not trajectory_data.empty:
                stats_df = pd.DataFrame()
                
                # Calculate statistics for numerical columns
                numeric_cols = trajectory_data.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    col_stats = {
                        'Mean': trajectory_data[col].mean(),
                        'Median': trajectory_data[col].median(),
                        'Std Dev': trajectory_data[col].std(),
                        'Min': trajectory_data[col].min(),
                        'Max': trajectory_data[col].max()
                    }
                    stats_df[col] = pd.Series(col_stats)
                
                stats_df.to_excel(writer, sheet_name='Statistics', index=True)
            
            # Analysis Results Sheet
            if analysis_results:
                # Convert the dictionary to a format suitable for DataFrame
                analysis_data = {
                    'Parameter': list(analysis_results.keys()),
                    'Value': list(analysis_results.values())
                }
                analysis_df = pd.DataFrame(analysis_data)
                analysis_df.to_excel(writer, sheet_name='Analysis Results', index=False)
            
            # Format the Excel file
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#D9E1F2',
                'border': 1
            })
            
            for worksheet in writer.sheets.values():
                worksheet.set_row(0, None, header_format)
                worksheet.autofit()
    
    elif format == 'csv':
        if not trajectory_data.empty:
            # Include basic statistics in CSV
            stats_df = pd.DataFrame()
            numeric_cols = trajectory_data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                col_stats = {
                    'Mean': trajectory_data[col].mean(),
                    'Median': trajectory_data[col].median(),
                    'Std Dev': trajectory_data[col].std(),
                    'Min': trajectory_data[col].min(),
                    'Max': trajectory_data[col].max()
                }
                stats_df[col] = pd.Series(col_stats)
            
            output.write(stats_df.to_csv(index=True).encode('utf-8'))
    
    # Reset buffer position
    output.seek(0)
    
    return output 