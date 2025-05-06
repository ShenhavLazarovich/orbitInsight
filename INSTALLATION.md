# Installation Guide for Satellite Trajectory Analysis Dashboard

This document provides detailed instructions for setting up and running the Satellite Trajectory Analysis Dashboard application.

## System Requirements

- **Python**: Version 3.10 or higher
- **PostgreSQL**: Version 12 or higher
- **Space-Track.org account**: Register at [https://www.space-track.org](https://www.space-track.org)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/satellite-trajectory-analysis.git
cd satellite-trajectory-analysis
```

### 2. Set Up Python Environment

#### Option A: Using venv (Virtual Environment)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Option B: Using conda

```bash
# Create a conda environment
conda create -n satellite-env python=3.10
conda activate satellite-env
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install numpy pandas plotly psycopg2-binary requests scipy sgp4 sqlalchemy streamlit trafilatura python-dotenv
```

### 4. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation

1. Install PostgreSQL following the instructions for your operating system from [postgresql.org](https://www.postgresql.org/download/)

2. Create a new database:
   ```bash
   createdb satellite_db
   ```

3. Set up the required tables (these will be automatically created when you first run the app)

#### Option B: Using a PostgreSQL Service (like AWS RDS, ElephantSQL, etc.)

1. Sign up for a PostgreSQL service of your choice
2. Create a new PostgreSQL database
3. Note the connection credentials (hostname, port, username, password, database name)

### 5. Configure Environment Variables

Create a `.env` file in the project root directory with the following variables:

```
# Database connection
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Space-Track.org credentials
SPACETRACK_USERNAME=your_username
SPACETRACK_PASSWORD=your_password
```

Alternatively, you can set these as environment variables in your system:

```bash
# On Windows (PowerShell)
$env:DATABASE_URL="postgresql://username:password@hostname:port/database_name"
$env:SPACETRACK_USERNAME="your_username"
$env:SPACETRACK_PASSWORD="your_password"

# On macOS/Linux
export DATABASE_URL="postgresql://username:password@hostname:port/database_name"
export SPACETRACK_USERNAME="your_username"
export SPACETRACK_PASSWORD="your_password"
```

### 6. Configure Streamlit

1. Create the Streamlit configuration directory:
   ```bash
   mkdir -p .streamlit
   ```

2. Create a configuration file at `.streamlit/config.toml` with the following content:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

## Running the Application

Start the Streamlit server:

```bash
streamlit run app.py
```

The application should now be running at `http://localhost:5000`

## Troubleshooting

### Database Connection Issues

- Verify your PostgreSQL instance is running
- Check that the DATABASE_URL environment variable is correctly formatted
- Ensure the database user has appropriate permissions

### Space-Track.org API Issues

- Verify your Space-Track.org credentials are correct
- Check your internet connection
- Ensure your Space-Track.org account has the necessary access permissions

### Python Dependency Issues

If you encounter errors related to missing packages or version conflicts:

```bash
pip install --upgrade pip
pip install --upgrade numpy pandas plotly psycopg2-binary requests scipy sgp4 sqlalchemy streamlit trafilatura python-dotenv
```

## Deploying to Production

### Option A: Deploying on a VPS (Virtual Private Server)

1. Set up a VPS with your provider of choice (AWS, DigitalOcean, Linode, etc.)
2. Install Python, PostgreSQL, and Git on the server
3. Clone the repository and follow the installation steps above
4. Use a process manager like Supervisor or PM2 to keep the application running

### Option B: Deploying with Docker

1. Build a Docker image using the provided Dockerfile
2. Run the container with appropriate environment variables
3. Map port 5000 to make the application accessible

### Option C: Deploying on Streamlit Cloud

1. Create an account on [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository
3. Configure the necessary secrets (database URL and Space-Track credentials)
4. Deploy the application