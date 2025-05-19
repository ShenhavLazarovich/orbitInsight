import os
from sqlalchemy import create_engine, text
from database import create_sample_satellite_data

def init_database():
    """Initialize the database with required tables and sample data."""
    # Get database connection parameters from environment variables or use defaults
    db_host = os.getenv("PGHOST", "localhost")
    db_port = os.getenv("PGPORT", "5432")
    db_name = os.getenv("PGDATABASE", "postgres")
    db_user = os.getenv("PGUSER", "postgres")
    db_password = os.getenv("PGPASSWORD", "postgres")
    
    # Create connection string
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        # Create database engine
        engine = create_engine(connection_string)
        
        # Create tables
        with engine.connect() as conn:
            # Create satellite_trajectories table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS satellite_trajectories (
                    id SERIAL PRIMARY KEY,
                    satellite_id VARCHAR(10) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    x FLOAT NOT NULL,
                    y FLOAT NOT NULL,
                    z FLOAT NOT NULL,
                    vx FLOAT,
                    vy FLOAT,
                    vz FLOAT,
                    altitude FLOAT,
                    alert_type VARCHAR(50),
                    alert_message TEXT
                )
            """))
            
            # Create index on satellite_id and timestamp
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_satellite_trajectories_sat_time 
                ON satellite_trajectories (satellite_id, timestamp)
            """))
            
            conn.commit()
        
        # Add sample data for known satellites
        satellites = [
            {
                "id": "25544",
                "name": "ISS (International Space Station)",
                "orbit_radius": 6771000,  # ~400km altitude
                "orbit_period": 92.68
            },
            {
                "id": "20580",
                "name": "Hubble Space Telescope",
                "orbit_radius": 6911000,  # ~540km altitude
                "orbit_period": 95
            },
            {
                "id": "99001",
                "name": "OpSat3000",
                "orbit_radius": 7071000,  # ~700km altitude
                "orbit_period": 100,
                "alt_variation": 0.1
            }
        ]
        
        for sat in satellites:
            create_sample_satellite_data(
                engine,
                sat["id"],
                sat["name"],
                sat["orbit_radius"],
                sat["orbit_period"],
                sat.get("alt_variation", 0.05)
            )
            
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database() 