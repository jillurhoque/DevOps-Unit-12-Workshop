import json
import requests

# --- Configuration ---
TENANT_ID = "7d6f97d6-d755-4c10-b763-409cc4b6638f"
CLIENT_ID = "7a00fe4e-46ac-4e25-b629-d4f01d9cfe98"   # consumer app (Weather App Consumer)
CLIENT_SECRET = ""                                # client secret value from app registration
API_APP_ID_URI = "api://09ac7cb7-9264-4c73-81dc-c7a51c4b11b9"
API_BASE_URL = "http://localhost:5000"

# --- Step 1: Get a token ---
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

token_response = requests.post(
    token_url,
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": f"{API_APP_ID_URI}/.default",
        "grant_type": "client_credentials",
    },
)

token_response.raise_for_status()
access_token = token_response.json()["access_token"]
print("Token acquired successfully.")

# --- Step 2: Call the WeatherForecast API ---
headers = {"Authorization": f"Bearer {access_token}"}

weather_response = requests.get(
    f"{API_BASE_URL}/WeatherForecast",
    headers=headers,
    verify=False,  # only for local dev certs; remove in production
)

# --- Step 3: Print the response ---
print(f"Status: {weather_response.status_code}")
print(json.dumps(weather_response.json(), indent=2))
