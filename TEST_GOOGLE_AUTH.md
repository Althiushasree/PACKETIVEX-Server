# Google Auth Implementation - Testing Guide

This document provides test cases and curl commands to verify the Google OAuth implementation.

## Pre-requisites for Testing

1. **Server running:** `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. **Valid Google ID Token** - Obtained from client after user authenticates with Google
3. **Environment configured** with valid `GOOGLE_CLIENT_ID`

---

## Test Scenarios

### Test 1: Successful Google Login (Valid Token & Domain)

**Scenario:** User logs in with valid Google token and cutmap.ac.in email

**Expected Behavior:**
- ✓ Token is validated
- ✓ Domain is verified (cutmap.ac.in)
- ✓ User is created in database (first login)
- ✓ JWT token is generated
- ✓ Response includes user info and JWT token
- ✓ Debug logs show all steps

**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_VALID_GOOGLE_ID_TOKEN_HERE"}'
```

**Expected Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userId": "1",
  "name": "John Doe",
  "email": "john.doe@cutmap.ac.in",
  "authMethod": "google",
  "message": null
}
```

**Debug Logs Should Show:**
```
✓ Token validation successful for email: john.doe@cutmap.ac.in
✓ New user created via Google Auth: john.doe@cutmap.ac.in
✓ Google login successful for: john.doe@cutmap.ac.in
```

---

### Test 2: Repeated Login (User Already Exists)

**Scenario:** Same user logs in again

**Expected Behavior:**
- ✓ Token is validated
- ✓ User is found in database (no duplicate creation)
- ✓ New JWT token is generated
- ✓ Response includes user info and new JWT token
- ✓ Debug logs show user was found, not created

**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"SAME_USER_GOOGLE_ID_TOKEN"}'
```

**Debug Logs Should Show:**
```
✓ Token validation successful for email: john.doe@cutmap.ac.in
User found in database: john.doe@cutmap.ac.in
✓ Google login successful for: john.doe@cutmap.ac.in
```

---

### Test 3: Invalid/Expired Token

**Scenario:** Token is malformed or expired

**Expected Behavior:**
- ✗ Token validation fails
- ✗ Response returns 401 Unauthorized
- ✗ Error message indicates invalid token
- ✓ Debug logs show validation failure

**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"invalid.token.here"}'
```

**Expected Response (401):**
```json
{
  "detail": "Invalid or expired Google token"
}
```

**Debug Logs Should Show:**
```
Invalid token format or signature: ...
Google token validation failed
```

---

### Test 4: Domain Validation Failed (Non-cutmap Email)

**Scenario:** Valid Google token but email is not @cutmap.ac.in

**Expected Behavior:**
- ✓ Token is valid
- ✗ Domain validation fails
- ✗ Response returns 403 Forbidden
- ✗ Error message indicates domain not allowed
- ✓ User is NOT created
- ✓ Debug logs show domain rejection

**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_WITH_OTHER_DOMAIN_EMAIL"}'
```

**Expected Response (403):**
```json
{
  "detail": "Only cutmap.ac.in domain emails are allowed"
}
```

**Debug Logs Should Show:**
```
Domain validation failed - Expected: cutmap.ac.in, Got: example.com for email: user@example.com
Domain validation failed for email: user@example.com
```

---

## Database Verification

### View Created Users

```sql
SELECT id, name, email, auth_method, created_at FROM users;
```

**Expected Output:**
```
id | name       | email                 | auth_method | created_at
1  | John Doe   | john.doe@cutmap.ac.in | google      | 1700000000000
2  | Jane Smith | jane.smith@cutmap.ac.in | google     | 1700000010000
```

---

## Debug Logging Verification

### Enable Debug Logging

In `.env`:
```ini
DEBUG_LOGGING=true
```

Restart server. Look for colored log output with timestamps:

```
2024-09-21 10:30:45 - [GOOGLE_AUTH] - DEBUG - Starting token validation (token length: 1234)
2024-09-21 10:30:45 - [google_auth] - DEBUG - Validating token against Google Client ID: 1234567890...
2024-09-21 10:30:46 - [google_auth] - INFO - ✓ Token validation successful for email: john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - DEBUG - [AUTH] domain_validation_success | email: joh***@cutmap.ac.in | 
2024-09-21 10:30:46 - [main] - DEBUG - [DB] SELECT on users | email=john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - INFO - ✓ New user created via Google Auth: john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - INFO - ✓ Google login successful for: john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - DEBUG - [RESPONSE] ✓ 200 /api/auth/google/login | email=john.doe@cutmap.ac.in, user_id=1
```

### Disable Debug Logging

In `.env`:
```ini
DEBUG_LOGGING=false
```

Output should only show INFO level:
```
2024-09-21 10:30:45 - [google_auth] - INFO - ✓ Token validation successful for email: john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - INFO - ✓ New user created via Google Auth: john.doe@cutmap.ac.in
2024-09-21 10:30:46 - [main] - INFO - ✓ Google login successful for: john.doe@cutmap.ac.in
```

---

## Other Endpoints Testing

### Test Dashboard (After Login)

**Get JWT Token from Google Login Response, then:**

```bash
curl -X GET http://localhost:8000/api/dashboard \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response (200):**
```json
{
  "totalPackets": 0,
  "totalBytes": 0,
  "activeConnections": 12,
  "openSockets": 8,
  "totalAlarms": 0
}
```

**Debug Logs Should Show:**
```
[REQUEST] GET /api/dashboard | no params
[DB] SELECT on packets
[RESPONSE] ✓ 200 /api/dashboard | packets=0, bytes=0
```

---

## Common Issues & Solutions

### Issue: "GOOGLE_CLIENT_ID not configured"

**Cause:** `GOOGLE_CLIENT_ID` not set in `.env`

**Solution:**
```ini
GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID
DEBUG_LOGGING=true
```

Then restart server and check debug logs.

### Issue: All tokens rejected as invalid

**Cause:** 
1. Token is from different Google project
2. Token is expired
3. Token signature mismatch

**Solution:**
- Verify token comes from same Google Cloud project
- Regenerate fresh token on client
- Check `GOOGLE_CLIENT_ID` matches project

### Issue: Domain validation failing for valid cutmap emails

**Cause:** `ALLOWED_EMAIL_DOMAIN` is wrong in `.env`

**Solution:**
```ini
ALLOWED_EMAIL_DOMAIN=cutmap.ac.in
```

(Note: lowercase, exact match)

### Issue: No debug logs appearing

**Cause:** 
1. `DEBUG_LOGGING` not set
2. Server not reloaded after `.env` change
3. Logs going to different stream

**Solution:**
```ini
DEBUG_LOGGING=true
```

Stop and restart server completely (not just reload).

---

## Performance Testing

### Login Response Time

**Command:**
```bash
time curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_TOKEN"}'
```

**Expected:** < 500ms for successful login

---

## Integration Testing

### End-to-End Flow

1. **Client gets Google ID Token** (from Google Sign-In)
2. **Client sends to backend:** `POST /api/auth/google/login`
3. **Backend validates token & domain**
4. **Backend creates/finds user**
5. **Backend returns JWT token**
6. **Client stores JWT token**
7. **Client uses JWT for authenticated requests** (e.g., `/api/dashboard`)

**Full Curl Test:**
```bash
# Step 1: Login with Google token
LOGIN_RESPONSE=$(curl -X POST http://localhost:8000/api/auth/google/login \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_TOKEN"}')

# Extract JWT token
JWT_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Step 2: Use JWT for authenticated request
curl -X GET http://localhost:8000/api/dashboard \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## Conclusion

The Google OAuth implementation provides:
- ✓ Secure token validation
- ✓ Domain-based authorization
- ✓ Automatic user creation
- ✓ JWT-based sessions
- ✓ Comprehensive debug logging
- ✓ Production-ready error handling

All endpoints maintain full functionality while logging is non-disruptive.

