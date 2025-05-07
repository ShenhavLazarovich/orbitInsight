# OrbitInsight: Advanced SpaceTrack.com Analysis Platform

A dynamic Streamlit-based platform for analyzing satellite movement and space object data from the Combined Space Operations Center (CSpOC) database with interactive visualization capabilities.

![Satellite Dashboard](generated-icon.png)

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/opsat3000)

## Features

- **Real-time satellite data**: Access actual satellite trajectory information from Space-Track.org
- **Interactive visualizations**: Analyze satellite orbits with 2D and 3D trajectory plots
- **Multiple data categories**: Explore satellite catalog, launch sites, decay events, conjunction warnings, and boxscore statistics
- **Anomaly detection**: Identify unusual satellite behavior with built-in analysis tools
- **Flexible filtering**: Search by satellite name, date range, and data types
- **Enhanced Earth reference visualization**: View satellites in relation to Earth with proper altitude scaling
- **PostgreSQL database**: Cache retrieved data for faster access and offline analysis

## Requirements

- Python 3.10+
- PostgreSQL database
- Space-Track.org account credentials

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/satellite-trajectory-analysis.git
   cd satellite-trajectory-analysis
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables for database connection and Space-Track.org credentials:
   ```
   # Database connection
   export DATABASE_URL=postgresql://username:password@localhost:5432/satellite_db
   
   # Space-Track.org credentials
   export SPACETRACK_USERNAME=your_username
   export SPACETRACK_PASSWORD=your_password
   ```

   Alternatively, you can set these environment variables in a `.env` file.

4. Create the Streamlit configuration directory and file:
   ```
   mkdir -p .streamlit
   ```

5. Add the following to `.streamlit/config.toml`:
   ```
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

## Usage

1. Start the Streamlit server:
   ```
   streamlit run app.py
   ```

2. Navigate to `http://localhost:5000` in your web browser

3. How to use the dashboard:
   - Select a data category from the sidebar (Satellite Trajectory, Catalog Data, etc.)
   - For Satellite Trajectory analysis:
     - **Type to search for satellites** - Start typing a satellite name in the search box
     - **Select with auto-complete** - As you type, matching satellite names will appear
     - **Auto-load data** - Press Enter after selecting a satellite to automatically load its data
     - Alternatively, set date range and alert types, then click "Load Data" button
     - Explore the visualizations across the different tabs
   - For other data categories:
     - Adjust filters as needed (days to look back, record limits, etc.)
     - Click the "Load Data" button for the selected category
     - Explore visualizations and download data as needed
   
4. Advanced features:
   - **3D Trajectory View**: View satellite orbits with Earth reference sphere and proper altitude scaling
   - **Altitude Profile**: Analyze orbital height variations over time
   - **Data Analysis**: Get orbit statistics and anomaly detection
   - **Data Export**: Download the trajectory data as CSV for further analysis

## Data Sources

This application retrieves data from:
- **Space-Track.org API**: Primary source for satellite information (requires account)
- **Local PostgreSQL database**: Caches retrieved data for faster access and offline use

## Error Handling

The application includes robust error handling for:
- Missing or invalid Space-Track.org credentials
- API connectivity issues
- Changed or unavailable API endpoints
- Missing or malformed data

If you encounter issues with specific data categories, the app will:
1. Attempt to use alternative API endpoints
2. Provide detailed error messages with troubleshooting information
3. Guide you to try different data categories if needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Space-Track.org for providing access to CSpOC satellite data
- The SGP4 propagator for trajectory calculations
- Streamlit, Pandas, and Plotly for the interactive dashboard framework

## Support the Project

If you find this tool useful for your satellite analysis needs, please consider supporting the project:

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/opsat3000)

Your support helps maintain and improve OrbitInsight!