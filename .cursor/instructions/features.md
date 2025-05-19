# Key Features (Revised)

- **Backend Proxy & Database**
  - All data requests are routed through a backend proxy (e.g., FastAPI/Flask).
  - The proxy fetches data from Space-Track.org only as often as allowed by their guidelines.
  - Data is cached and stored in a local database (e.g., PostgreSQL, SQLite, or Redis).
  - The database holds: Satellite catalog (SATCAT), TLEs, Boxscore, Conjunction (CDM) data, Launch sites, Decay data.

- **Data Freshness & Compliance**
  - Each data type is refreshed only at the allowed frequency (e.g., SATCAT once per day after 17:00 UTC).
  - The UI displays the last update time and next eligible refresh for each dataset.
  - Users cannot force a refresh before the allowed window.

- **User Authentication**
  - Users log in to OrbitInsight (not directly to Space-Track.org).
  - No user credentials for Space-Track.org are ever exposed or required.

- **Data Visualization & Analytics**
  - Interactive dashboards for satellite trajectories, catalog search, conjunction risk, launch sites, boxscore, and decay statistics.
  - All visualizations use data from the local database, not direct API calls.

- **Data Export & Reporting**
  - Users can export tables and visualizations as CSV, PDF, or images.
  - Exports are generated from the cached database.

- **Feedback & Support**
  - In-app feedback form, stored in a local feedback table. 