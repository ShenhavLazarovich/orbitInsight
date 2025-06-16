# OrbitInsight UI Documentation (Revised)

## Overview
OrbitInsight is a Streamlit-based dashboard for analyzing and visualizing satellite data from Space-Track.org. The UI is designed for compliance, clarity, and user experience, with all data served from a local database.

## Authentication
- **Login Form:**
  - Users log in to OrbitInsight (not Space-Track.org)
  - No user-provided Space-Track credentials
  - Secure local authentication only

## Layout Structure

### 1. Navigation
- **Sidebar:**
  - Navigation menu with all available pages
  - User info display (logged-in username)
  - Logout button
  - Clean separation with horizontal rule

### 2. Data Freshness Indicators
- Each page displays:
  - "Data last updated: [timestamp]"
  - "Next update available: [timestamp]"
  - If a user tries to refresh early, show: "Per Space-Track.org policy, this data can only be refreshed after [timestamp]."

### 3. Main Dashboard
- **Welcome Header:**
  - Large title and subtitle
  - Centered layout
- **Platform Capabilities Section:**
  - Feature cards for real-time data access, interactive visualization, advanced analysis, and optimized performance
- **How to Use Section:**
  - Tutorial card with numbered instructions
- **Summary Analysis Section:**
  - Quick stats and recent activity

### 4. Data Pages
- All data visualizations and tables are generated from the local database
- Download/export buttons for each table/visualization
- Error handling for unavailable or out-of-date data

### 5. Feedback
- Sidebar form for submitting feedback, stored in the `feedback` table 