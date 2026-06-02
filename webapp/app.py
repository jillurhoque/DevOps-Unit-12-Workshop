import os
import json
import base64
import msal
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
from functools import wraps
import app_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')
Session(app)

SCOPES = [app_config.SCOPE]


def _decode_jwt_payload(token):
    """Decode JWT payload without signature verification (debug only)."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None):
    """Build MSAL client application."""
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        client_credential=app_config.CLIENT_SECRET,
        authority=app_config.AUTHORITY,
        token_cache=cache)


def _build_auth_code_flow(scopes=None):
    """Build authorization code flow object."""
    return _build_msal_app().initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scopes=None):
    """Get token from cache if available."""
    cache = _load_cache()
    msal_app = _build_msal_app(cache=cache)
    accounts = msal_app.get_accounts()
    if accounts:
        result = msal_app.acquire_token_silent(scopes or [], account=accounts[0])
        _save_cache(cache)
        return result
    return None


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    """Home page."""
    if session.get("user"):
        return redirect(url_for("weather"))
    return redirect(url_for("login"))


@app.route("/login")
def login():
    """Initiate login flow."""
    session["flow"] = _build_auth_code_flow(scopes=SCOPES)
    return redirect(session["flow"]["auth_uri"])


@app.route(app_config.REDIRECT_PATH)
def authorized():
    """Authorization callback handler."""
    try:
        cache = _load_cache()
        msal_app = _build_msal_app(cache=cache)
        result = msal_app.acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return f"Login failed: {result.get('error_description')}", 400
        claims = result.get("id_token_claims", {})
        session["user"] = {
            "name": claims.get("name") or claims.get("preferred_username") or "Signed-in user"
        }
        # Keep immediate token as fallback in case account lookup is unavailable.
        session["access_token"] = result.get("access_token")
        _save_cache(cache)
    except ValueError as e:
        return f"Auth flow error: {e}", 400
    return redirect(url_for("weather"))


@app.route("/weather")
@login_required
def weather():
    """Get and display weather forecast from API."""
    try:
        # Get token for API access
        token_result = _get_token_from_cache(scopes=SCOPES)

        access_token = None
        if token_result and "error" in token_result:
            return f"Error acquiring token: {token_result.get('error_description')}", 400
        if token_result and token_result.get("access_token"):
            access_token = token_result.get("access_token")
        elif session.get("access_token"):
            access_token = session.get("access_token")
        else:
            return redirect(url_for("login"))
        
        # Call the weather API
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            app_config.API_ENDPOINT,
            headers=headers,
            verify=False  # Only for local dev; remove in production
        )
        
        if response.status_code == 200:
            weather_data = response.json()
        else:
            token_claims = _decode_jwt_payload(access_token)
            weather_data = {
                "error": f"API request failed: {response.status_code}",
                "api_response": response.text,
                "token_aud": token_claims.get("aud"),
                "token_scp": token_claims.get("scp"),
                "token_roles": token_claims.get("roles"),
            }
        
        return render_template(
            "weather.html",
            user=session.get("user"),
            weather=weather_data
        )
    
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    return redirect(app_config.AUTHORITY + "/oauth2/v2.0/logout?" +
                    "post_logout_redirect_uri=" + url_for("index", _external=True))


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="localhost")
