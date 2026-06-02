"""
Configuration for the Flask OAuth2 app
"""

# Azure AD configuration
TENANT_ID = "7d6f97d6-d755-4c10-b763-409cc4b6638f"  # From your app registration
CLIENT_ID = "ad2f46a9-87ca-4c67-89ec-7c4a6e4b11f6"  # Webapp app registration client ID
CLIENT_SECRET = "2Tz8Q~VGbKCgnT8Hklo-KuoSlQ3l_0b4JXew5cEm"  # Client secret from webapp app registration
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Redirect path after login
REDIRECT_PATH = "/getAToken"

# API configuration
API_APP_ID_URI = "api://09ac7cb7-9264-4c73-81dc-c7a51c4b11b9"  # From the Weather API app registration
SCOPE = f"{API_APP_ID_URI}/access_as_user"  # The scope you created in step 3.1
API_ENDPOINT = "http://localhost:5000/WeatherForecast"

# Session secret key (should be random and secure in production)
SECRET_KEY = "dev"
