# User Guide: Satellite Trajectory Analysis Dashboard

This guide will help you navigate and make the most of the Satellite Trajectory Analysis Dashboard.

## Getting Started

After launching the application, you'll see the main dashboard interface with a sidebar for navigation and controls.

### Main Interface Components

1. **Sidebar**: Contains data category selection and filtering controls
2. **Main Panel**: Displays visualizations and data tables
3. **Download Buttons**: Allow you to export data for further analysis

## Data Categories

The application provides access to several data categories from the Combined Space Operations Center (CSpOC) database:

### 1. Satellite Trajectory Data

This is the primary view for analyzing satellite movements.

#### How to Use:

1. Select "Satellite Trajectory" from the sidebar dropdown
2. Choose a satellite from the dropdown list (sorted by launch date, newest first)
3. Set the date range for analysis using the date pickers
4. Select any alert types you want to include
5. Click "Load Data" to retrieve and visualize the trajectory

#### Available Visualizations:

- **2D Trajectory**: Shows the satellite's path projected onto the X-Y plane
- **3D Trajectory**: Displays the complete orbital path in 3D space
- **Altitude Profile**: Graphs the satellite's altitude over time
- **Parameter Time Series**: Plots selected parameters against time
- **Alert Distribution**: Shows the distribution of different alert types (if selected)
- **Anomaly Detection**: Highlights unusual behaviors in the trajectory

### 2. Catalog Data

Comprehensive information about satellites in the Space-Track catalog.

#### How to Use:

1. Select "Catalog Data" from the sidebar dropdown
2. Adjust the "Number of records" slider to set how many entries to retrieve
3. Click "Load Catalog Data" to fetch the information

#### Available Information:

- Satellite names and NORAD IDs
- Launch dates and sites
- Orbital parameters
- Operational status
- Country of origin

### 3. Launch Sites Data

Information about global satellite launch facilities.

#### How to Use:

1. Select "Launch Sites Data" from the sidebar dropdown
2. Click "Load Launch Sites Data" to retrieve the information

#### Available Information:

- Launch site names and locations
- Countries
- Number of launches
- Site status

### 4. Decay Data

Information about objects that have re-entered Earth's atmosphere.

#### How to Use:

1. Select "Decay Data" from the sidebar dropdown
2. Adjust the "Days to look back" slider to set the historical time period
3. Adjust the "Number of records" slider to set how many entries to retrieve
4. Click "Load Decay Data" to fetch the information

#### Available Information:

- Object names and NORAD IDs
- Decay dates and times
- Pre-decay orbital parameters
- Re-entry prediction accuracy

### 5. Conjunction Data

Information about close approaches between space objects.

#### How to Use:

1. Select "Conjunction Data" from the sidebar dropdown
2. Adjust the "Days to look back" slider to set the historical time period
3. Adjust the "Number of records" slider to set how many entries to retrieve
4. Click "Load Conjunction Data" to fetch the information
5. If data is available, you can filter by "Minimum Collision Probability"

#### Available Visualizations:

- Distribution of miss distances
- Conjunction events timeline
- Detailed tabular data with object identifiers

### 6. Boxscore Data

Statistical summary of space objects by country.

#### How to Use:

1. Select "Boxscore Data" from the sidebar dropdown
2. Click "Load Boxscore Data" to retrieve the information

#### Available Visualizations:

- Bar chart of objects by country
- Pie chart of payload vs. debris distribution
- Detailed tables with country-specific statistics

## Advanced Features

### Data Export

Each data view includes a "Download as CSV" button that allows you to save the data for offline analysis.

### Anomaly Detection

For trajectory data, you can:

1. Select a parameter for anomaly detection
2. Adjust the Z-score threshold slider
3. View highlighted anomalies in the trajectory

### Trajectory Metrics

The trajectory view automatically calculates key metrics including:

- Orbital period
- Average altitude
- Eccentricity
- Inclination
- Alert frequency (if alerts are included)

## Troubleshooting

### Missing Data

If you see a "No data found" message:

1. Try selecting a different date range
2. Verify your Space-Track.org credentials
3. Try a different data category
4. Check your internet connection

### API Connection Issues

If you see a connection error:

1. The application will automatically try alternative API endpoints
2. Check the error message for specific details
3. Verify your Space-Track.org account has the necessary permissions

### Visualization Errors

If a visualization fails to display:

1. The raw data table will still be available for viewing
2. Check for any error messages that explain the issue
3. Try adjusting the date range or filters to get a different data sample

## Tips for Best Results

1. **Start with recent dates** for more reliable data
2. **Popular satellites** like the ISS (NORAD ID: 25544) or Hubble (NORAD ID: 20580) have the most comprehensive data
3. **Download data** you want to preserve, as the application cache may be cleared
4. **Try different visualizations** for a more complete understanding of the satellite's behavior