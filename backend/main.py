from fastapi import FastAPI, HTTPException
import httpx
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone

load_dotenv()

# Load Firebase credentials from JSON file
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
    raise ValueError(f"Firebase credentials file not found at {FIREBASE_CREDENTIALS_PATH}.")

with open(FIREBASE_CREDENTIALS_PATH, "r") as f:
    firebase_credentials = json.load(f)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="OrbitInsight Backend Proxy")

SPACE_TRACK_API_URL = "https://www.space-track.org/api"
SPACE_TRACK_USERNAME = os.getenv("SPACE_TRACK_USERNAME")
SPACE_TRACK_PASSWORD = os.getenv("SPACE_TRACK_PASSWORD")

# Initialize scheduler
scheduler = BackgroundScheduler()

async def fetch_and_cache_satcat():
    """
    Fetch SATCAT data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch SATCAT data
        satcat_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/satcat"
        satcat_response = await client.get(satcat_url)
        if satcat_response.status_code != 200:
            print("Failed to fetch SATCAT data.")
            return

        # Cache SATCAT data in Firebase Firestore
        satcat_data = satcat_response.json()
        db.collection("satcat").document("latest").set({"data": satcat_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"SATCAT data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_tle():
    """
    Fetch TLE data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch TLE data
        tle_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/tle"
        tle_response = await client.get(tle_url)
        if tle_response.status_code != 200:
            print("Failed to fetch TLE data.")
            return

        # Cache TLE data in Firebase Firestore
        tle_data = tle_response.json()
        db.collection("tle").document("latest").set({"data": tle_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"TLE data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_boxscore():
    """
    Fetch Boxscore data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch Boxscore data
        boxscore_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/boxscore"
        boxscore_response = await client.get(boxscore_url)
        if boxscore_response.status_code != 200:
            print("Failed to fetch Boxscore data.")
            return

        # Cache Boxscore data in Firebase Firestore
        boxscore_data = boxscore_response.json()
        db.collection("boxscore").document("latest").set({"data": boxscore_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"Boxscore data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_cdm():
    """
    Fetch CDM data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch CDM data
        cdm_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/cdm"
        cdm_response = await client.get(cdm_url)
        if cdm_response.status_code != 200:
            print("Failed to fetch CDM data.")
            return

        # Cache CDM data in Firebase Firestore
        cdm_data = cdm_response.json()
        db.collection("cdm").document("latest").set({"data": cdm_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"CDM data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_launch_sites():
    """
    Fetch Launch Sites data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch Launch Sites data
        launch_sites_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/launch_sites"
        launch_sites_response = await client.get(launch_sites_url)
        if launch_sites_response.status_code != 200:
            print("Failed to fetch Launch Sites data.")
            return

        # Cache Launch Sites data in Firebase Firestore
        launch_sites_data = launch_sites_response.json()
        db.collection("launch_sites").document("latest").set({"data": launch_sites_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"Launch Sites data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_decay():
    """
    Fetch Decay data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch Decay data
        decay_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/decay"
        decay_response = await client.get(decay_url)
        if decay_response.status_code != 200:
            print("Failed to fetch Decay data.")
            return

        # Cache Decay data in Firebase Firestore
        decay_data = decay_response.json()
        db.collection("decay").document("latest").set({"data": decay_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"Decay data updated at {datetime.now(timezone.utc)}")

async def fetch_and_cache_satellite_data(norad_id: int):
    """
    Fetch data for a specific satellite by its NORAD ID from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        print("Space-Track.org credentials not configured.")
        return

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print("Failed to login to Space-Track.org.")
            return

        # Fetch satellite data
        satellite_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/satcat/NORAD_CAT_ID/{norad_id}"
        satellite_response = await client.get(satellite_url)
        if satellite_response.status_code != 200:
            print(f"Failed to fetch data for satellite NORAD ID {norad_id}.")
            return

        # Cache satellite data in Firebase Firestore
        satellite_data = satellite_response.json()
        db.collection("satellites").document(str(norad_id)).set({"data": satellite_data, "last_updated": firestore.SERVER_TIMESTAMP})
        print(f"Data for satellite NORAD ID {norad_id} updated at {datetime.now(timezone.utc)}")

@app.get("/satcat")
async def get_satcat():
    """
    Fetch SATCAT data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch SATCAT data
        satcat_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/satcat"
        satcat_response = await client.get(satcat_url)
        if satcat_response.status_code != 200:
            raise HTTPException(status_code=satcat_response.status_code, detail="Failed to fetch SATCAT data.")

        # Cache SATCAT data in Firebase Firestore
        satcat_data = satcat_response.json()
        db.collection("satcat").document("latest").set({"data": satcat_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return satcat_data

@app.get("/tle")
async def get_tle():
    """
    Fetch TLE data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch TLE data
        tle_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/tle"
        tle_response = await client.get(tle_url)
        if tle_response.status_code != 200:
            raise HTTPException(status_code=tle_response.status_code, detail="Failed to fetch TLE data.")

        # Cache TLE data in Firebase Firestore
        tle_data = tle_response.json()
        db.collection("tle").document("latest").set({"data": tle_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return tle_data

@app.get("/boxscore")
async def get_boxscore():
    """
    Fetch Boxscore data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch Boxscore data
        boxscore_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/boxscore"
        boxscore_response = await client.get(boxscore_url)
        if boxscore_response.status_code != 200:
            raise HTTPException(status_code=boxscore_response.status_code, detail="Failed to fetch Boxscore data.")

        # Cache Boxscore data in Firebase Firestore
        boxscore_data = boxscore_response.json()
        db.collection("boxscore").document("latest").set({"data": boxscore_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return boxscore_data

@app.get("/cdm")
async def get_cdm():
    """
    Fetch CDM data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch CDM data
        cdm_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/cdm"
        cdm_response = await client.get(cdm_url)
        if cdm_response.status_code != 200:
            raise HTTPException(status_code=cdm_response.status_code, detail="Failed to fetch CDM data.")

        # Cache CDM data in Firebase Firestore
        cdm_data = cdm_response.json()
        db.collection("cdm").document("latest").set({"data": cdm_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return cdm_data

@app.get("/launch_sites")
async def get_launch_sites():
    """
    Fetch Launch Sites data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch Launch Sites data
        launch_sites_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/launch_sites"
        launch_sites_response = await client.get(launch_sites_url)
        if launch_sites_response.status_code != 200:
            raise HTTPException(status_code=launch_sites_response.status_code, detail="Failed to fetch Launch Sites data.")

        # Cache Launch Sites data in Firebase Firestore
        launch_sites_data = launch_sites_response.json()
        db.collection("launch_sites").document("latest").set({"data": launch_sites_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return launch_sites_data

@app.get("/decay")
async def get_decay():
    """
    Fetch Decay data from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch Decay data
        decay_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/decay"
        decay_response = await client.get(decay_url)
        if decay_response.status_code != 200:
            raise HTTPException(status_code=decay_response.status_code, detail="Failed to fetch Decay data.")

        # Cache Decay data in Firebase Firestore
        decay_data = decay_response.json()
        db.collection("decay").document("latest").set({"data": decay_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return decay_data

@app.get("/satellite/{norad_id}")
async def get_satellite_data(norad_id: int):
    """
    Fetch data for a specific satellite by its NORAD ID from Space-Track.org and cache it in Firebase Firestore.
    """
    if not SPACE_TRACK_USERNAME or not SPACE_TRACK_PASSWORD:
        raise HTTPException(status_code=500, detail="Space-Track.org credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Login to Space-Track.org
        login_url = f"{SPACE_TRACK_API_URL}/ajaxauth/login"
        login_data = {
            "identity": SPACE_TRACK_USERNAME,
            "password": SPACE_TRACK_PASSWORD
        }
        login_response = await client.post(login_url, data=login_data)
        if login_response.status_code != 200:
            raise HTTPException(status_code=login_response.status_code, detail="Failed to login to Space-Track.org.")

        # Fetch satellite data
        satellite_url = f"{SPACE_TRACK_API_URL}/basicspacedata/query/class/satcat/NORAD_CAT_ID/{norad_id}"
        satellite_response = await client.get(satellite_url)
        if satellite_response.status_code != 200:
            raise HTTPException(status_code=satellite_response.status_code, detail=f"Failed to fetch data for satellite NORAD ID {norad_id}.")

        # Cache satellite data in Firebase Firestore
        satellite_data = satellite_response.json()
        db.collection("satellites").document(str(norad_id)).set({"data": satellite_data, "last_updated": firestore.SERVER_TIMESTAMP})

        return satellite_data

# Schedule data updates (once/day after 17:00 UTC)
scheduler.add_job(fetch_and_cache_satcat, CronTrigger(hour=17, minute=0, timezone=timezone.utc))
scheduler.add_job(fetch_and_cache_tle, CronTrigger(hour=17, minute=0, timezone=timezone.utc))
scheduler.add_job(fetch_and_cache_boxscore, CronTrigger(hour=17, minute=0, timezone=timezone.utc))
scheduler.add_job(fetch_and_cache_cdm, CronTrigger(hour=17, minute=0, timezone=timezone.utc))
scheduler.add_job(fetch_and_cache_launch_sites, CronTrigger(hour=17, minute=0, timezone=timezone.utc))
scheduler.add_job(fetch_and_cache_decay, CronTrigger(hour=17, minute=0, timezone=timezone.utc))

# Start the scheduler
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 