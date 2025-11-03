# Google Authentication Setup Guide

## Problem: Google Sign-In Not Working

Your Google authentication may not be working due to one of these reasons:

1. **Client ID not properly configured**
2. **Authorized origins not set up**
3. **Client ID expired or revoked**
4. **CORS/Origin issues**

---

## Step-by-Step Fix

### 1. Check Browser Console

First, open your browser's Developer Tools (F12) and check the Console tab when you load the page. Look for errors like:

- ❌ `idpiframe_initialization_failed`
- ❌ `popup_closed_by_user`
- ❌ `access_denied`
- ❌ `invalid_client`

### 2. Configure Google Cloud Console

You need to set up your Google OAuth credentials properly:

#### A. Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project (or create a new one)

#### B. Enable Google Sign-In API
1. Go to **APIs & Services** → **Library**
2. Search for "Google Identity"
3. Click **"Google+ API"** or **"Google Identity Services"**
4. Click **ENABLE**

#### C. Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Google Workspace)
3. Fill in required fields:
   - App name: "Horror Oracle" (or your app name)
   - User support email: Your email
   - Developer contact: Your email
4. Click **SAVE AND CONTINUE**
5. Skip scopes (click **SAVE AND CONTINUE**)
6. Add test users (your Gmail account)
7. Click **SAVE AND CONTINUE**

#### D. Create OAuth 2.0 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Application type: **Web application**
4. Name: "Horror Oracle Web Client"
5. **Authorized JavaScript origins** - ADD THESE:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   http://localhost
   ```
6. **Authorized redirect URIs** - ADD THIS:
   ```
   http://localhost:5000
   ```
7. Click **CREATE**
8. **COPY the Client ID** (it looks like: `123456789-abcdef.apps.googleusercontent.com`)

### 3. Update Your Code

Replace the Client ID in `index.html` (line 1742):

```javascript
client_id: 'YOUR_NEW_CLIENT_ID_HERE.apps.googleusercontent.com',
```

**Current Client ID in your code:**
```
383630092112-5vqj924hq2n44tjk1gpb3bisokfab50m.apps.googleusercontent.com
```

### 4. Test the Setup

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Clear localStorage**:
   - Open DevTools (F12) → Console
   - Run: `localStorage.clear()`
3. **Restart your Flask server**:
   ```bash
   python horror.py
   ```
4. **Open in browser**: http://localhost:5000
5. **Check console** for these messages:
   - ✅ `Google Sign-In initialized successfully`
6. **Click the Google Sign-In button**

---

## Common Errors & Solutions

### Error: "idpiframe_initialization_failed"
**Solution:** Your origin is not authorized. Add `http://localhost:5000` to Authorized JavaScript origins.

### Error: "popup_closed_by_user"
**Solution:** User closed the popup. This is normal - just try signing in again.

### Error: "invalid_client"
**Solution:** Your Client ID is invalid or expired. Create a new one in Google Cloud Console.

### Error: "access_denied"
**Solution:** Your email is not added as a test user. Add it in OAuth consent screen.

### Error: "redirect_uri_mismatch"
**Solution:** Add your redirect URI to the authorized list in Google Cloud Console.

### No button appears / Script doesn't load
**Solution:** 
1. Check your internet connection
2. Check if Google services are blocked by firewall/ad blocker
3. Try accessing https://accounts.google.com/gsi/client directly

---

## Quick Debug Test

Add this to your browser console to test if Google Sign-In loads:

```javascript
if (typeof google !== 'undefined' && google.accounts) {
    console.log('✅ Google Sign-In library loaded');
} else {
    console.log('❌ Google Sign-In library NOT loaded');
}
```

---

## Alternative: Test with a Simple HTML Page

Create a file called `test-google-signin.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Google Sign-In Test</title>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
  <h1>Google Sign-In Test</h1>
  <div id="g_id_onload"
       data-client_id="YOUR_CLIENT_ID_HERE"
       data-callback="handleCredentialResponse">
  </div>
  <div class="g_id_signin" data-type="standard"></div>
  
  <script>
    function handleCredentialResponse(response) {
      console.log("Encoded JWT ID token: " + response.credential);
      const userInfo = JSON.parse(atob(response.credential.split('.')[1]));
      console.log("User info:", userInfo);
      alert("Signed in as: " + userInfo.email);
    }
  </script>
</body>
</html>
```

Replace `YOUR_CLIENT_ID_HERE` and open this file in your browser.

---

## Still Not Working?

### Option 1: Check if your Client ID is valid
Run this in your browser console:
```javascript
fetch('https://oauth2.googleapis.com/tokeninfo?client_id=383630092112-5vqj924hq2n44tjk1gpb3bisokfab50m.apps.googleusercontent.com')
  .then(r => r.json())
  .then(d => console.log('Client ID status:', d))
  .catch(e => console.error('Client ID error:', e));
```

### Option 2: Use Firebase Authentication (Alternative)
If Google Sign-In continues to fail, consider using Firebase Authentication which provides a simpler setup.

### Option 3: Create a new Google Cloud Project
Sometimes the easiest fix is to start fresh:
1. Create a new project in Google Cloud Console
2. Follow steps 2B-2D above
3. Use the new Client ID

---

## Contact & Support

If you're still having issues:
1. Check the browser console for specific error messages
2. Verify your Google Cloud Console settings
3. Make sure you're testing on `http://localhost:5000` (not a different port)
4. Try a different browser (Chrome, Firefox, Edge)

**Common Port Issues:**
- If running on port 5000 but accessing via 3000, update authorized origins
- Make sure Flask is running: `python horror.py`
- Check if port is accessible: `http://localhost:5000` should show your app

