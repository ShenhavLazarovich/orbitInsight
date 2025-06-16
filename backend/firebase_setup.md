# Setting Up Firebase Firestore for OrbitInsight

## Overview
This guide walks you through setting up Firebase Firestore for caching data in OrbitInsight. Firebase Firestore is a NoSQL database that allows you to store, query, and sync data in real-time.

## Steps

### 1. Create a Firebase Project
- Go to the [Firebase Console](https://console.firebase.google.com/).
- Click **Add project** and follow the prompts to create a new project (e.g., `OrbitInsight`).

### 2. Enable Firestore
- In the Firebase Console, select your project.
- In the left sidebar, click **Firestore Database**.
- Click **Create database**.
- Choose **Start in production mode** (or **Start in test mode** for development).
- Select a location for your database (e.g., `us-central1`).
- Click **Enable**.

### 3. Generate a Service Account Key
- In the Firebase Console, go to **Project settings** (gear icon).
- Navigate to the **Service accounts** tab.
- Click **Generate new private key**.
- Save the downloaded JSON file (e.g., `firebase-credentials.json`) in the `backend/` directory.

### 4. Configure Environment Variables
- Create a `.env` file in the `backend/` directory.
- Add the following variables:
  ```
  SPACE_TRACK_USERNAME=your_username
  SPACE_TRACK_PASSWORD=your_password
  FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
  ```
  **Note:** Replace the placeholder values with your actual Space-Track.org credentials. The `FIREBASE_CREDENTIALS_PATH` should point to your Firebase service account JSON file.

### 5. Install Firebase Admin SDK
- Ensure the Firebase Admin SDK is installed:
  ```sh
  pip install firebase-admin
  ```

### 6. Test the Setup
- Run the backend:
  ```sh
  uvicorn main:app --reload
  ```
- Call the `/satcat` endpoint to fetch and cache SATCAT data in Firestore.

## Next Steps
- Add endpoints for other data types (TLE, Boxscore, CDM, Launch Sites, Decay).
- Implement data update policy and scheduling for other data types. 