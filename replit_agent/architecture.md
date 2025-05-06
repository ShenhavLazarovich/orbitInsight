# Architecture Overview

## Overview

This project is a Satellite Trajectory Analysis Dashboard that allows users to visualize and analyze satellite trajectory data from the Combined Space Operations Center (CSpOC) database via the Space-Track.org API. The application fetches satellite data, performs analysis, and presents it through an interactive web interface. Users can filter data by satellite name, time period, and alert types, and can explore multiple categories of space object data including satellite catalogs, launch sites, decay events, conjunction messages, and boxscore statistics.

## System Architecture

The system follows a three-tier architecture:

1. **Presentation Layer**: A Streamlit-based web interface that allows users to interact with the application.
2. **Application Layer**: Python-based data processing, analysis, and visualization logic.
3. **Data Layer**: PostgreSQL database for caching and Space-Track.org API for live data.

The application is designed to run as a standalone web service, with Streamlit handling both the frontend UI and backend processing. This architecture provides a straightforward development experience and deployment model.

## Key Components

### Frontend

- **Streamlit Application** (`app.py`): The main entry point that creates the web interface. It handles user input, data display, and visualization rendering.
- **Visualization Module** (`visualization.py`): Contains functions for creating various types of data visualizations using Plotly.

### Backend

- **Database Module** (`database.py`): Manages database connections and queries. Uses SQLAlchemy for database operations and implements caching for Space-Track data.
- **Space-Track API Module** (`space_track.py`): Handles authentication and data retrieval from the Space-Track.org API using the SGP4 propagator for trajectory calculations.
- **Analysis Module** (`analysis.py`): Contains functions for analyzing satellite trajectory data, calculating statistics, and deriving insights.
- **Utilities Module** (`utils.py`): Provides helper functions for data formatting, conversion, and calculations.

### Data Model

The application works with a PostgreSQL database containing multiple tables:
- `satellite_trajectories`: Stores satellite trajectory data including position coordinates and timestamps.
- `satellite_catalog`: Caches information about available satellites.
- `alerts`: Stores alert information related to satellite trajectories.

The application also interfaces with multiple Space-Track.org API endpoints to retrieve different categories of data.

## Data Flow

1. **User Selection**: User selects a data category and applies filters from the Streamlit UI.
2. **Data Retrieval**: The application first checks the local PostgreSQL database for cached data.
3. **API Fallback**: If data is not available locally, the application contacts the Space-Track.org API.
4. **Data Processing**: Raw data is processed and analyzed to extract meaningful metrics.
5. **Data Caching**: Retrieved API data is stored in the database for future use.
6. **Visualization**: The processed data is visualized through various plots and charts.
7. **User Interaction**: Users can further filter data, adjust views, and download results.

The general flow is as follows:
```
User → Streamlit Interface → Local DB Query → [If needed] Space-Track API → Data Processing → Visualization → User Interface
```

## External Dependencies

The project relies on several key Python libraries:

- **Streamlit**: Powers the web interface and interactive elements
- **Pandas**: Handles data processing and manipulation
- **Plotly**: Creates interactive visualizations
- **SQLAlchemy**: Manages database connections and queries
- **NumPy/SciPy**: Performs numerical and statistical calculations
- **SGP4**: Satellite trajectory propagation from Two-Line Element sets
- **Requests**: HTTP requests to the Space-Track.org API
- **Trafilatura**: Web scraping capabilities for additional data sources

## Error Handling and Fallbacks

The application implements a robust error handling system:

1. **API Connection Errors**: Multiple retry mechanisms with informative user messages
2. **Changing API Endpoints**: Alternative endpoint attempts when primary endpoints fail
3. **Missing Data**: Fallback to sample data when API data is unavailable
4. **Error Visualization**: User-friendly error messages with troubleshooting suggestions
5. **Detailed Logging**: Comprehensive error logging for debugging

## Deployment Strategy

The application is configured for deployment in several ways:

1. **Replit Deployment**: The application is configured to run on Replit with specific settings for Python and PostgreSQL.

2. **Streamlit Cloud Deployment**: The application can be deployed to Streamlit's cloud service, with configuration in the `.streamlit` directory.

3. **Standalone Deployment**: The application can be deployed to any server with Python and PostgreSQL, using environment variables for configuration.

The deployment process follows these steps:
- The Streamlit server runs on port 5000
- The server is configured in headless mode to run without a browser
- The application is bound to all network interfaces (`0.0.0.0`)

## Development Considerations

### Database Configuration

The database connection is configured to be flexible, supporting both:
- A single `DATABASE_URL` environment variable
- Individual PostgreSQL connection parameters (`PGHOST`, `PGPORT`, etc.)

This approach allows for easy deployment across different environments without code changes.

### API Authentication

Space-Track.org API authentication uses environment variables for credentials:
- `SPACETRACK_USERNAME`: Username for Space-Track.org
- `SPACETRACK_PASSWORD`: Password for Space-Track.org

### Scalability

The current architecture has some considerations for scalability:
- Database caching reduces the load on the Space-Track.org API
- Multiple fallback mechanisms improve reliability
- Error handling ensures graceful degradation when services are unavailable

For further scaling, implementing additional caching, background processing, or horizontal scaling would be beneficial.

### Future Extensions

The modular design allows for easy extension in several directions:
- Adding more data categories from Space-Track.org or other sources
- Implementing predictive analytics for collision risk assessment
- Developing real-time monitoring capabilities
- Adding user authentication and customized dashboards
- Integrating with other space situational awareness systems