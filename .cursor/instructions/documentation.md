# OrbitInsight Documentation (Revised)

## Architecture
OrbitInsight uses a backend proxy and a local database to cache and serve all Space-Track.org data. The Streamlit UI never calls the Space-Track.org API directly. All data is fetched, cached, and rate-limited by the backend proxy, then served to the frontend from the local database.

## Data Update Policy
- **SATCAT, Boxscore, Launch Sites:** Updated once per day after 17:00 UTC.
- **TLE:** Updated once per hour per satellite.
- **CDM:** Updated 3x/day for all, 1x/hour for specific events.
- **Decay:** Updated once per week.
- Each table in the database has a `last_updated` timestamp.
- The UI displays the last update and next eligible refresh for each dataset.

## Database Schema (Example)
- `satcat` (satellite catalog)
- `tle` (two-line elements)
- `boxscore`
- `cdm` (conjunction data)
- `launch_sites`
- `decay`
- `feedback`

## Compliance
- All data is fetched and cached in accordance with [Space-Track.org API guidelines](https://www.space-track.org/documentation#/api).
- No direct user access to the API; all requests are mediated and rate-limited by the backend proxy.
- Data is never shared or transferred in violation of Space-Track.org terms.

## User Experience
- Users see the latest available data and are informed of update schedules.
- If a user tries to refresh early, the UI blocks the request and explains why.
- All downloads and exports are generated from the local database. 