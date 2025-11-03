# 🩸 Google OAuth Sign-In Fix Guide

## Problem
The Google Sign-In popup appears but shows an error and closes immediately when clicked.

## Common Causes & Solutions

### 1. ⚠️ **Authorized JavaScript Origins Missing**

**Go to:** [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

1. Click on your OAuth 2.0 Client ID
2. Under **Authorized JavaScript origins**, make sure you have:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
3. If running on a different port, add that too (e.g., `http://localhost:8000`)
4. Click **SAVE**

### 2. ⚠️ **Authorized Redirect URIs Missing**

In the same OAuth 2.0 Client ID settings:

1. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
2. Also add the generic OAuth callback:
   ```
   http://localhost:5000/oauth2callback
   http://127.0.0.1:5000/oauth2callback
   ```
3. Click **SAVE**

### 3. ⚠️ **Pop-up Blockers**

- Make sure your browser is not blocking pop-ups from `localhost`
- Check browser console for "popup_blocked" errors
- Temporarily disable any ad blockers

### 4. ⚠️ **Client ID Issues**

Your current Client ID:
```
383630092112-5vqj924hq2n44tjk1gpb3bisokfab50m.apps.googleusercontent.com
```

Verify this is correct in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### 5. ⚠️ **OAuth Consent Screen**

Make sure you've configured the OAuth consent screen:

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (for testing)
3. Fill in:
   - App name: "Horror Oracle"
   - User support email: Your email
   - Developer contact: Your email
4. Add test users if in testing mode
5. Click **SAVE AND CONTINUE**

---

## Testing Steps

### Step 1: Open Browser Console
Press `F12` and go to the **Console** tab

### Step 2: Check for Errors
When you click the Google Sign-In button, look for:
- ❌ `popup_closed` - User closed the popup
- ❌ `popup_failed_to_open` - Browser blocked the popup
- ❌ `idpiframe_initialization_failed` - Configuration error
- ❌ `access_denied` - User denied permission

### Step 3: Test Page
Open this file in your browser:
```
http://localhost:5000/test-google-signin.html
```

This will show detailed diagnostic information.

---

## Quick Fix Commands

### Restart Flask Server
```bash
# Stop the server (Ctrl+C)
# Then restart:
python horror.py
```

### Clear Browser Cache
```javascript
// Run in browser console:
localStorage.clear();
sessionStorage.clear();
location.reload();
```

---

## Still Not Working?

### Check These:

1. **Are you serving from the correct URL?**
   - Must be exactly `http://localhost:5000` or `http://127.0.0.1:5000`
   - NOT `http://localhost:5000/` with trailing slash in origins

2. **Did you save changes in Google Cloud Console?**
   - Click the blue **SAVE** button at the bottom
   - Wait 5 minutes for changes to propagate

3. **Is the OAuth consent screen published?**
   - If in testing mode, you must add test users
   - Or publish the app

4. **Browser issues?**
   - Try incognito/private mode
   - Try a different browser
   - Disable browser extensions

---

## Expected Console Output

When working correctly, you should see:
```
✅ Google Sign-In library loaded successfully
✅ Google Sign-In initialized successfully
📍 Current origin: http://localhost:5000
🔐 handleCredentialResponse called
📝 Decoding JWT token...
✅ JWT decoded successfully
✅ User signed in successfully: [Your Name]
```

---

## Need More Help?

Check the browser console for detailed error messages. The enhanced error handler will now show:
- Error type
- Error message
- Detailed stack trace

Copy the error and search for it along with "Google Sign-In" for specific solutions.

---

## Emergency Fallback

If OAuth still doesn't work, you can temporarily bypass it:

1. Open `index.html`
2. Comment out the Google Sign-In section
3. Add a test user manually in `horror.py`

(Note: This is only for development testing - don't use in production!)

