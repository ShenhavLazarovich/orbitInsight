# Architecture Overview

## Overview

This project is a Satellite Trajectory Analysis Dashboard that allows users to visualize and analyze satellite trajectory data. The application fetches satellite trajectory data from a PostgreSQL database, performs various analyses on this data, and presents it through an interactive web interface. Users can filter data by satellite ID and time period, view trajectory visualizations, and download processed data.

## System Architecture

The system follows a simple three-tier architecture:

1. **Presentation Layer**: A Streamlit-based web interface that allows users to interact with the application.
2. **Application Layer**: Python-based data processing, analysis, and visualization logic.
3. **Data Layer**: PostgreSQL database storing satellite trajectory information.

The application is designed to run as a standalone web service, with Streamlit handling both the frontend UI and backend processing. This architecture provides a straightforward development experience and deployment model.

## Key Components

### Frontend

- **Streamlit Application** (`app.py`): The main entry point that creates the web interface. It handles user input, data display, and visualization rendering.
- **Visualization Module** (`visualization.py`): Contains functions for creating various types of data visualizations using Plotly.

### Backend

- **Database Module** (`database.py`): Manages database connections and queries. Uses SQLAlchemy for database operations.
- **Analysis Module** (`analysis.py`): Contains functions for analyzing satellite trajectory data, calculating statistics, and deriving insights.
- **Utilities Module** (`utils.py`): Provides helper functions for data formatting, conversion, and calculations.

### Data Model

The application appears to work with a PostgreSQL database containing at least one table:
- `satellite_trajectories`: Stores satellite trajectory data including position coordinates and timestamps.

Based on the code, the data includes:
- Satellite positions (x, y coordinates)
- Timestamps
- Satellite identifiers

## Data Flow

1. **Data Retrieval**: The application connects to a PostgreSQL database to fetch trajectory data for specific satellites.
2. **Data Processing**: Raw trajectory data is processed and analyzed to extract meaningful metrics.
3. **Visualization**: The processed data is visualized through various plots and charts.
4. **User Interaction**: Users can filter data, adjust views, and download results through the Streamlit interface.

The general flow is as follows:
```
User → Streamlit Interface → Data Query → Database → Data Processing → Visualization → User Interface
```

## External Dependencies

The project relies on several key Python libraries:

- **Streamlit**: Powers the web interface and interactive elements
- **Pandas**: Handles data processing and manipulation
- **Plotly**: Creates interactive visualizations
- **SQLAlchemy**: Manages database connections and queries
- **NumPy/SciPy**: Performs numerical and statistical calculations

These dependencies are managed through the `pyproject.toml` file, which specifies version requirements for each package.

## Deployment Strategy

The application is configured for deployment in several ways:

1. **Replit Deployment**: The `.replit` file indicates the application is set up to run on Replit, with specific configuration for Python 3.11.

2. **Streamlit Cloud Deployment**: The application can be deployed to Streamlit's cloud service, as indicated by the Streamlit configuration files.

3. **Containerized Deployment**: The application could be containerized and deployed to any container orchestration platform, though no Docker configuration is present in the repository.

The deployment process follows these steps:
- The Streamlit server runs on port 5000 (configurable)
- The server is configured in headless mode to run without a browser
- The application is bound to all network interfaces (`0.0.0.0`)

## Development Considerations

### Database Configuration

The database connection is configured to be flexible, supporting both:
- A single `DATABASE_URL` environment variable
- Individual PostgreSQL connection parameters (`PGHOST`, `PGPORT`, etc.)

This approach allows for easy deployment across different environments without code changes.

### Scalability

The current architecture has some limitations for high-scale deployments:
- Data processing happens in the same process as the web server
- There's no caching mechanism evident in the code
- Large datasets might cause performance issues in the current implementation

For scaling to larger datasets or more users, implementing caching, background processing, or horizontal scaling would be beneficial.

### Future Extensions

The modular design allows for easy extension in several directions:
- Adding more complex analysis algorithms
- Supporting additional visualization types
- Integrating with other data sources beyond PostgreSQL
- Implementing user authentication and multi-user support