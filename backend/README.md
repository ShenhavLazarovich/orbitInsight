# OrbitInsight Backend Proxy

## Overview
This is the backend proxy for OrbitInsight, responsible for fetching data from Space-Track.org, caching it in Firebase Firestore, and serving it to the Streamlit UI.

## Setup

### 1. Install Dependencies
```sh
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the `backend/` directory with the following variables:
```
SPACE_TRACK_USERNAME=your_username
SPACE_TRACK_PASSWORD=your_password
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```
**Note:** Replace the placeholder values with your actual Space-Track.org credentials. The `FIREBASE_CREDENTIALS_PATH` should point to your Firebase service account JSON file.

### 3. Run the Backend
```sh
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`.

## API Endpoints

### GET /satcat
Fetches SATCAT data from Space-Track.org and caches it in Firebase Firestore.

### GET /tle
Fetches TLE data from Space-Track.org and caches it in Firebase Firestore.

### GET /boxscore
Fetches Boxscore data from Space-Track.org and caches it in Firebase Firestore.

### GET /cdm
Fetches CDM data from Space-Track.org and caches it in Firebase Firestore.

### GET /launch_sites
Fetches Launch Sites data from Space-Track.org and caches it in Firebase Firestore.

### GET /decay
Fetches Decay data from Space-Track.org and caches it in Firebase Firestore.

### GET /satellite/{norad_id}
Fetches data for a specific satellite by its NORAD ID from Space-Track.org and caches it in Firebase Firestore.

## Data Update Policy
- SATCAT data is updated once per day after 17:00 UTC using APScheduler.
- TLE data is updated once per day after 17:00 UTC using APScheduler.
- Boxscore data is updated once per day after 17:00 UTC using APScheduler.
- CDM data is updated once per day after 17:00 UTC using APScheduler.
- Launch Sites data is updated once per day after 17:00 UTC using APScheduler.
- Decay data is updated once per day after 17:00 UTC using APScheduler.

## Next Steps
- Implement data update policy and scheduling for other data types. 