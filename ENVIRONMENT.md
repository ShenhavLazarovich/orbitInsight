# Environment Variables

This document lists all environment variables required by the Satellite Trajectory Analysis Dashboard. These can be set in your system environment or in a `.env` file in the project root directory.

## Required Environment Variables

### Database Connection

The application requires a PostgreSQL database. You can configure it using either:

**Option 1**: A single DATABASE_URL (preferred)
```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

**Option 2**: Individual connection parameters
```
PGHOST=hostname
PGPORT=5432
PGUSER=username
PGPASSWORD=password
PGDATABASE=database_name
```

### Space-Track.org API Access

To retrieve real satellite data, you need Space-Track.org credentials:
```
SPACETRACK_USERNAME=your_space_track_username
SPACETRACK_PASSWORD=your_space_track_password
```

You can register for a Space-Track.org account at [https://www.space-track.org/auth/login](https://www.space-track.org/auth/login).

## Optional Environment Variables

### Application Configuration
```
DEBUG=True  # Enable debug mode with additional logging
SAMPLE_DATA_ONLY=True  # Use only sample data, don't connect to Space-Track API
MAX_CACHE_DAYS=30  # Number of days to cache API data
```

## Example .env File

Create a file named `.env` in the project root directory with contents similar to:

```
# Database connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/satellite_db

# Space-Track.org credentials
SPACETRACK_USERNAME=your_username@example.com
SPACETRACK_PASSWORD=your_secure_password

# Optional configuration
DEBUG=False
MAX_CACHE_DAYS=30
```

## Notes

- The `.env` file should NEVER be committed to version control
- For production deployment, use your platform's secure environment variable storage
- Ensure your Space-Track.org account has the necessary permissions for the data you want to access