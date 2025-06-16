# Refactoring Plan for OrbitInsight

## Overview
This plan outlines the steps to refactor OrbitInsight according to the new instructions. The goal is to ensure all data is fetched via a backend proxy, cached in Firebase Firestore, and served to the Streamlit UI in compliance with Space-Track.org API guidelines.

## Steps

### 1. **Backend Proxy Setup** [Completed]
- **Objective:** Create a backend proxy (e.g., FastAPI/Flask) to handle all requests to Space-Track.org.
- **Tasks:**
  - Set up a new backend project (e.g., `backend/` directory).
  - Implement API endpoints for each data type (SATCAT, TLE, Boxscore, CDM, Launch Sites, Decay).
  - Ensure the proxy respects Space-Track.org's rate limits and terms of use.
  - Add logging and error handling for API requests.
- **Note:** FastAPI backend is now set up with a `/satcat` endpoint. Next, implement caching in Firebase Firestore.

### 2. **Local Database Setup** [Completed]
- **Objective:** Create a local database to cache all data fetched by the backend proxy.
- **Tasks:**
  - Choose a database (e.g., PostgreSQL, SQLite, Redis).
  - Define the database schema for each data type (e.g., `satcat`, `tle`, `boxscore`, `cdm`, `launch_sites`, `decay`, `feedback`).
  - Implement database connection and CRUD operations in the backend proxy.
  - Add a `last_updated` timestamp to each table to track data freshness.
- **Note:** Firebase Firestore is now used for caching data. The `/satcat` endpoint caches data in Firestore.

### 3. **Data Update Policy Implementation** [Completed]
- **Objective:** Ensure data is refreshed only at the allowed frequency.
- **Tasks:**
  - Implement a scheduler (e.g., using `apscheduler` or `cron`) to trigger data updates at the specified intervals.
  - For each data type, enforce the update policy (e.g., SATCAT once/day after 17:00 UTC).
  - Log update times and next eligible refresh times.
- **Note:** APScheduler is now used to update SATCAT data once per day after 17:00 UTC.

### 4. **Streamlit UI Refactoring**
- **Objective:** Update the Streamlit UI to fetch data from Firebase Firestore instead of directly calling the Space-Track.org API.
- **Tasks:**
  - Remove any direct API calls from the Streamlit UI.
  - Update the UI to display data freshness indicators (e.g., "Data last updated: [timestamp]").
  - Implement error handling for unavailable or out-of-date data.
  - Ensure all exports and downloads are generated from Firebase Firestore.

### 5. **User Authentication**
- **Objective:** Implement secure local authentication for OrbitInsight.
- **Tasks:**
  - Create a login form for users to log in to OrbitInsight (not Space-Track.org).
  - Store user credentials securely (e.g., using environment variables or a secure database).
  - Ensure no user credentials for Space-Track.org are ever exposed or required.

### 6. **Testing & Validation**
- **Objective:** Ensure the refactored system works as expected and complies with Space-Track.org guidelines.
- **Tasks:**
  - Write unit tests for the backend proxy, database operations, and UI components.
  - Perform integration tests to verify data flow from the backend proxy to Firebase Firestore to the UI.
  - Validate compliance with Space-Track.org API guidelines.

### 7. **Documentation & Deployment**
- **Objective:** Update documentation and prepare for deployment.
- **Tasks:**
  - Update the PRD, features, documentation, and UI instructions to reflect the new architecture.
  - Prepare deployment scripts or instructions for the backend proxy, Firebase Firestore, and Streamlit UI.
  - Ensure all dependencies and configurations are documented.

## Timeline
- **Week 1:** Backend Proxy Setup & Local Database Setup
- **Week 2:** Data Update Policy Implementation & Streamlit UI Refactoring
- **Week 3:** User Authentication & Testing & Validation
- **Week 4:** Documentation & Deployment

## Success Criteria
- All data is fetched via the backend proxy and cached in Firebase Firestore.
- The Streamlit UI displays data freshness indicators and complies with Space-Track.org guidelines.
- User authentication is secure and does not require Space-Track.org credentials.
- All tests pass, and the system is ready for deployment. 