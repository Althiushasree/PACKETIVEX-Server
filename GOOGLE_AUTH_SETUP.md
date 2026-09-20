# Google OAuth Authentication Setup Guide

This document explains how to set up and use Google OAuth authentication with the PACKETIVEX server.

## Overview

The server now uses **Google OAuth 2.0** for authentication with automatic domain validation. Only emails with the **cutmap.ac.in** domain are allowed to log in.

### Key Features

✓ Google OAuth 2.0 ID token validation  
✓ Domain-based authorization (cutmap.ac.in)  
✓ Automatic user creation on first login  
✓ JWT token generation for session management  
✓ Comprehensive debug logging without disrupting functionality  
✓ Backward compatible with legacy email/password endpoints (deprecated)

---

## Prerequisites

1. **Google Cloud Project** - Create one at [Google Cloud Console](https://console.cloud.google.com/)
2. **OAuth 2.0 Client ID** - Configure OAuth credentials for web application
3. **Python 3.9+** and dependencies from `requirements.txt`

---

## Google Cloud Setup (One-time)

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name: `PACKETIVEX-Auth`
4. Click "Create"

### Step 2: Enable Google+ API

1. In the Console, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and press **Enable**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. If prompted, click **Configure Consent Screen** first:
   - Choose **External** for user type
   - Fill in app name: `PACKETIVEX`
   - Add authorized domain: `cutmap.ac.in`
   - Save and continue
4. Back to Credentials, click **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web application**
6. Add Authorized redirect URIs (for your app frontend):
   - `http://localhost:3000`
   - `https://yourdomain.com/auth/callback`
   - Add any other URLs where your client runs
7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

---

## Server Configuration

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-auth>=2.25.0` - Google authentication library
- `PyJWT>=2.8.0` - JWT token generation
- `python-jose>=3.3.0` - JWT utilities

### Step 2: Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```ini
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
API_KEY=nt04-network-admin-secret-token

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/network_intelligence
# Or for SQLite testing:
# DATABASE_URL=sqlite:///./network_intelligence.db

# Google OAuth Configuration
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
ALLOWED_EMAIL_DOMAIN=cutmap.ac.in

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production

# Debug Logging
DEBUG_LOGGING=true
```

**Replace:**
- `YOUR_CLIENT_ID_HERE` - Your Google OAuth Client ID
- `YOUR_CLIENT_SECRET_HERE` - Your Google OAuth Client Secret (⚠️ Keep secret!)
- `your-secret-key-change-in-production` - A strong random string (use 32+ characters)

### Step 3: Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server starts at: `http://localhost:8000`

---

## Client Usage

### 1. Get Google ID Token

Your frontend/client must first obtain a Google ID token. Here's how with different methods:

#### Using Google Sign-In JavaScript Library

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>

<div id="g_id_onload"
     data-client_id="YOUR_CLIENT_ID_HERE"
     data-callback="handleCredentialResponse">
</div>
<div class="g_id_signin" data-type="standard"></div>

<script>
function handleCredentialResponse(response) {
    const idToken = response.credential; // This is the ID token
    
    // Send to your backend
    fetch('/api/auth/google/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ token: idToken })
    })
    .then(r => r.json())
    .then(data => {
        // Save the JWT token returned
        localStorage.setItem('auth_token', data.token);
        console.log('Login successful:', data);
    });
}
</script>
```

#### Using Google Auth Library (Node.js)

```javascript
const { OAuth2Client } = require('google-auth-library');

const client = new OAuth2Client('YOUR_CLIENT_ID_HERE');

async function getIdToken(accessToken) {
    const ticket = await client.verifyIdToken({
        idToken: accessToken,
        audience: 'YOUR_CLIENT_ID_HERE'
    });
    return ticket.getPayload();
}
```

### 2. Send Token to Backend

**Endpoint:** `POST /api/auth/google/login`

**Request:**
```json
{
    "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImZvbyIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": "123",
    "name": "John Doe",
    "email": "john.doe@cutmap.ac.in",
    "authMethod": "google"
}
```

**Error Responses:**

- **401 Unauthorized** - Invalid or expired token
```json
{"detail": "Invalid or expired Google token"}
```

- **403 Forbidden** - Email domain not allowed
```json
{"detail": "Only cutmap.ac.in domain emails are allowed"}
```

### 3. Use JWT Token for Authenticated Requests

Include the JWT token in subsequent API requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/dashboard
```

---

## Debug Logging

The server includes comprehensive debug logging that can be toggled via the `DEBUG_LOGGING` environment variable.

### Enable Debug Logging

```ini
DEBUG_LOGGING=true
```

### Sample Debug Output

```
2024-01-15 10:30:45 - [google_auth] - DEBUG - Starting token validation (token length: 1234)
2024-01-15 10:30:45 - [google_auth] - DEBUG - Validating token against Google Client ID: 1234567890...
2024-01-15 10:30:46 - [google_auth] - DEBUG - Token signature verified. Subject (user ID): 987654321
2024-01-15 10:30:46 - [google_auth] - DEBUG - Extracted email from token: john.doe@cutmap.ac.in
2024-01-15 10:30:46 - [google_auth] - INFO - ✓ Token validation successful for email: john.doe@cutmap.ac.in
2024-01-15 10:30:46 - [main] - DEBUG - [AUTH] domain_validation_success | email: joh***@cutmap.ac.in | 
2024-01-15 10:30:46 - [main] - DEBUG - [DB] SELECT on users | email=john.doe@cutmap.ac.in
2024-01-15 10:30:46 - [main] - INFO - ✓ New user created via Google Auth: john.doe@cutmap.ac.in
2024-01-15 10:30:46 - [main] - INFO - ✓ Google login successful for: john.doe@cutmap.ac.in
```

### Disable Debug Logging

```ini
DEBUG_LOGGING=false
```

This reduces output to INFO level only, improving performance in production.

---

## Database

The `users` table now tracks authentication method:

```sql
SELECT * FROM users;
```

Example output:
```
id | name      | email              | hashed_password | is_active | auth_method | created_at
1  | John Doe  | john@cutmap.ac.in  | google_oauth    | true      | google      | 1700000000000
```

---

## Migration from Email/Password (if applicable)

The old email/password endpoints are deprecated but still available for backward compatibility:

- `POST /api/auth/register` - Deprecated
- `POST /api/auth/login` - Deprecated

To migrate existing users:

1. **Preserve existing data** - All user records remain
2. **Gradual transition** - Both authentication methods work during migration
3. **Update clients** - Use new `/api/auth/google/login` endpoint
4. **Remove deprecated endpoints** - After migration is complete

---

## Troubleshooting

### Issue: "Invalid or expired Google token"

**Causes:**
- Token is expired (valid for ~1 hour)
- Token format is incorrect
- Token was not signed by Google
- `GOOGLE_CLIENT_ID` doesn't match the token

**Solution:**
- Regenerate token on client side
- Verify `GOOGLE_CLIENT_ID` in `.env` matches Google Cloud Console
- Check debug logs: `DEBUG_LOGGING=true`

### Issue: "Only cutmap.ac.in domain emails are allowed"

**Cause:** User email domain doesn't match `ALLOWED_EMAIL_DOMAIN`

**Solution:**
- Ensure user has a cutmap.ac.in email account
- Check `ALLOWED_EMAIL_DOMAIN` value in `.env`
- To allow other domains, update `.env`: `ALLOWED_EMAIL_DOMAIN=example.com`

### Issue: Secret key configuration errors

**Cause:** `SECRET_KEY` not set or too short

**Solution:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then add to `.env`:
```ini
SECRET_KEY=generated-key-here
```

### Issue: No debug logs showing

**Check:**
1. Ensure `DEBUG_LOGGING=true` in `.env`
2. Reload/restart the server after changing `.env`
3. Check log output on console (not just files)

---

## Security Best Practices

1. **Never commit secrets:**
   - Add `.env` to `.gitignore`
   - Keep `GOOGLE_CLIENT_SECRET` and `SECRET_KEY` confidential

2. **Use HTTPS in production:**
   - Configure SSL certificates
   - Update redirect URIs to use `https://`

3. **Rotate secrets regularly:**
   - Change `SECRET_KEY` every 90 days
   - Regenerate Google OAuth credentials if compromised

4. **Validate email domain:**
   - Current setup only allows `cutmap.ac.in`
   - Change via `ALLOWED_EMAIL_DOMAIN` if needed

5. **Monitor authentication logs:**
   - Enable debug logging in non-production
   - Track failed login attempts

---

## API Reference

### POST /api/auth/google/login

Google OAuth login endpoint.

**Request:**
```json
{
    "token": "string (Google ID token from client)"
}
```

**Response (200 - Success):**
```json
{
    "token": "string (JWT token for authenticated requests)",
    "userId": "string (database user ID)",
    "name": "string (user name)",
    "email": "string (user email)",
    "authMethod": "google",
    "message": null
}
```

**Response (401 - Invalid Token):**
```json
{
    "detail": "Invalid or expired Google token"
}
```

**Response (403 - Domain Not Allowed):**
```json
{
    "detail": "Only cutmap.ac.in domain emails are allowed"
}
```

---

## Support & Questions

For issues or questions:
1. Check debug logs: `DEBUG_LOGGING=true`
2. Review error messages in response
3. Verify `.env` configuration
4. Check Google Cloud Console for credential setup

