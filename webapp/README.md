# Weather Forecast Web App - OAuth2 Implementation

This is a Flask web application that implements the OAuth2 authorization code flow to access a protected Weather Forecast API.

## Setup Instructions

### Step 1: Prerequisites

Make sure you have completed Parts 1 and 2 of the workshop. You should have:
- A protected Weather API running locally
- An app registration for the API
- An app registration for a consumer application

### Step 2: Create an App Registration for the Webapp

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to **App registrations** and create a new app
3. Name it `Weather App Webapp - <Your Initials>`
4. Set **Supported account types** to "Accounts in this organizational directory only"
5. Click **Register**

### Step 3: Configure Authentication

1. In your new app registration, go to **Authentication** (left menu)
2. Click **Add a platform** → **Web**
3. Set the Redirect URI to `http://localhost:5000/getAToken`
4. Check "Access tokens" and "ID tokens"
5. Click **Configure**

### Step 4: Create a Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Set expiration and click **Add**
4. Copy the secret value (you won't be able to see it again!)

### Step 5: Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **My APIs** → Select your Weather API app
4. Select **Delegated permissions**
5. Check `access_as_user` (you created this scope in the API app registration)
6. Click **Add permissions**
7. **Request admin consent** from your trainer/admin

### Step 6: Update the API

The API needs to be updated to accept delegated user permissions in addition to application permissions:

1. Open `WeatherForecast/Startup.cs`
2. You should already have both `ApplicationPolicy` and `UserPolicy` policies defined
3. The `WeatherForecastController` should use `[Authorize(Policy = "UserPolicy")]`

If you need to test the script from Part 2 again, you can temporarily change the policy back to `ApplicationPolicy`.

### Step 7: Configure the Webapp

1. Install dependencies:
   ```bash
   cd webapp
   pip install -r requirements.txt
   ```

2. Edit `app_config.py` and fill in your configuration:
   - `TENANT_ID`: Your Azure tenant ID (from any app registration overview)
   - `CLIENT_ID`: Your webapp app registration client ID
   - `API_APP_ID_URI`: The application ID URI from your Weather API app registration (format: `api://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
   - `API_ENDPOINT`: Keep as `http://localhost:5000/WeatherForecast` if running locally

### Step 8: Run the Application

1. Make sure your Weather API is running:
   ```bash
   cd WeatherForecast
   dotnet run
   ```

2. In another terminal, run the Flask app:
   ```bash
   cd webapp
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

4. Click **Login** and follow the Microsoft Entra ID login flow

5. Once logged in, you should see the weather forecast!

## How It Works

### OAuth2 Authorization Code Flow

1. **User clicks Login** → Redirected to Microsoft Entra ID login page
2. **User authenticates** → Microsoft Entra ID redirects back to `/getAToken`
3. **App exchanges auth code for token** → MSAL library handles this
4. **Token stored in session** → Used to make API calls
5. **App calls Weather API** → Using the user's token
6. **API validates token** → Checks that it has the `access_as_user` scope
7. **Weather data displayed** → User sees the forecast

### Key Differences from Part 2 (Client Credentials Flow)

| Feature | Client Credentials (Part 2) | Authorization Code (Part 3) |
|---------|---------------------------|--------------------------|
| Flow Type | App-to-app | App-on-behalf-of-user |
| Authentication | Client secret | User login |
| Token Claims | `roles` claim | `scp` claim with `access_as_user` |
| Policy | `ApplicationPolicy` | `UserPolicy` |
| Scope | `api://.../.default` | `api://.../access_as_user` |

## Troubleshooting

### "Certificate verify failed" error
If you get SSL certificate errors:
- Option 1: Run `dotnet dev-certs https --trust` in the WeatherForecast directory
- Option 2: The code already has `verify=False` for local development

### "Invalid scope" error
Make sure you:
1. Created the `access_as_user` scope in the API app registration → Expose an API
2. Added the delegated permission in the webapp app registration → API permissions
3. Have admin consent granted

### "Unauthorized (401)" accessing the API
Make sure:
1. The `WeatherForecastController` is using `[Authorize(Policy = "UserPolicy")]`
2. Your `appsettings.json` has the correct tenant ID and client ID
3. Admin consent has been granted for the webapp's API permissions

### User can't login
Make sure:
1. The redirect URI in the webapp app registration matches `http://localhost:5000/getAToken`
2. Your `TENANT_ID` in `app_config.py` is correct
3. Your `CLIENT_ID` in `app_config.py` matches your webapp app registration

## Production Considerations

Before deploying to production:
1. Remove `verify=False` from the API calls and use proper certificate verification
2. Use a strong, random secret key in `app.config['SECRET_KEY']`
3. Set `app.run(debug=False)`
4. Use HTTPS for all endpoints
5. Store sensitive configuration in environment variables or a secure vault
6. Implement proper token refresh logic
7. Add error handling and logging
8. Consider token caching strategies
