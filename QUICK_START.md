# Quick Start Guide - Google OAuth Authentication

## 🚀 5-Minute Setup

### 1. Get Google OAuth Credentials (Google Cloud Console)
```
1. Go to console.cloud.google.com
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 Client ID (Web)
5. Copy Client ID and Secret
```

### 2. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
ALLOWED_EMAIL_DOMAIN=cutmap.ac.in
SECRET_KEY=generate-a-strong-secret-key
DEBUG_LOGGING=true
```

### 3. Install & Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test Login
```bash
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_GOOGLE_ID_TOKEN"}'
```

---

## 📝 API Reference

### Login with Google Token
```
POST /api/auth/google/login

Request:
{
  "token": "google_id_token_from_client"
}

Response (200):
{
  "token": "jwt_token_for_auth_requests",
  "userId": "1",
  "name": "John Doe",
  "email": "john.doe@cutmap.ac.in",
  "authMethod": "google"
}

Errors:
- 401: Invalid/expired token
- 403: Domain not allowed (only cutmap.ac.in)
```

### Use JWT for Authenticated Requests
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/dashboard
```

---

## 🔍 Debug Logging

### Enable
```ini
DEBUG_LOGGING=true
```

Shows:
- Token validation steps
- Domain checks
- User creation/lookup
- Database operations
- Request/response details

### Disable (Production)
```ini
DEBUG_LOGGING=false
```

Only INFO level messages.

---

## 📦 What's New

| File | Changes |
|------|---------|
| `app/main.py` | Added `/api/auth/google/login` + logging to all endpoints |
| `app/google_auth.py` | NEW: Google token validation & domain checks |
| `app/logger.py` | NEW: Structured debug logging |
| `app/auth.py` | JWT token generation & verification |
| `app/models.py` | Added `auth_method` field to User |
| `requirements.txt` | +6 new dependencies (google-auth, PyJWT, etc.) |
| `.env.example` | Google OAuth configuration |

---

## ✅ Key Features

✓ Google OAuth 2.0 token validation  
✓ Automatic domain restriction (cutmap.ac.in)  
✓ Auto-creates user on first login  
✓ JWT-based session management  
✓ Comprehensive debug logging (non-disruptive)  
✓ All existing endpoints still work  
✓ Production-ready error handling  

---

## 🔐 Security

- Token signature verified with Google's public keys
- Only cutmap.ac.in emails allowed
- JWT tokens expire after 24 hours
- No plain passwords stored
- API keys preserved
- Secrets managed via environment variables

---

## 📋 Flow Diagram

```
Client (with Google Account)
    ↓
1. User clicks "Sign in with Google"
    ↓
2. Google returns ID token to client
    ↓
3. Client sends ID token to POST /api/auth/google/login
    ↓
Backend:
    ├─ Validate token signature with Google
    ├─ Extract email from token
    ├─ Check email domain is cutmap.ac.in
    ├─ Create user in DB (if new)
    ├─ Generate JWT token
    └─ Return JWT to client
    ↓
4. Client stores JWT in localStorage
    ↓
5. Client sends JWT in Authorization header for all API requests
    ↓
Backend validates JWT and serves request
```

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| "Invalid token" | Token is expired or GOOGLE_CLIENT_ID mismatch |
| "Domain not allowed" | Email is not @cutmap.ac.in (this is by design) |
| No debug logs | Set `DEBUG_LOGGING=true` and restart server |
| Can't import modules | Run `pip install -r requirements.txt` |

---

## 📚 Documentation

- **GOOGLE_AUTH_SETUP.md** - Complete setup guide
- **TEST_GOOGLE_AUTH.md** - Testing scenarios & curl commands
- **IMPLEMENTATION_SUMMARY.md** - Technical overview
- **QUICK_START.md** - This file

---

## 🧪 Quick Test

```bash
# After server is running:

# 1. Check health
curl http://localhost:8000/api/health

# 2. List apps (no auth needed for this example)
curl http://localhost:8000/api/analytics/applications

# 3. Try login with invalid token (will fail as expected)
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"test"}'

# Expected response: 
# {"detail":"Invalid or expired Google token"}
```

---

## 📞 Support

See full documentation for:
- Google Cloud setup details
- Advanced configuration
- Troubleshooting
- Database queries
- Performance tuning
- Security best practices

---

**Status: ✅ Ready for Use**

All files are created, configured, and ready to deploy.

