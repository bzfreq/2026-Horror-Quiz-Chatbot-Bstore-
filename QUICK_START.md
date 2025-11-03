# 🩸 Horror Oracle - Quick Start Guide

## Problem: "The app had a problem restart"

This error means Google is blocking your sign-in because your email is not authorized.

## 🔴 ONE-MINUTE FIX

### For Windows Users:

1. **Double-click:** `FIX_GOOGLE_AUTH.bat`
2. This will:
   - Open Google Cloud Console in your browser
   - Show you what to do
   - Start the Flask server
3. **Follow the on-screen instructions**

### Manual Fix (All Platforms):

1. **Go to:** https://console.cloud.google.com/apis/credentials/consent

2. **Add yourself as a test user:**
   - Scroll down to **"Test users"**
   - Click **"+ ADD USERS"**
   - Enter **YOUR email address**
   - Click **SAVE**

3. **Wait 3-5 minutes** (very important!)

4. **Start the server:**
   ```bash
   python horror.py
   ```

5. **Test it:**
   - Open: http://localhost:5000/test-google-auth-detailed.html
   - Click "Sign in with Google"
   - Should work now!

---

## If Still Not Working

### Option 1: Publish the App (Recommended)

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click **"PUBLISH APP"**
3. Confirm
4. Wait 5 minutes
5. Try again

### Option 2: Verify JavaScript Origins

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Under **"Authorized JavaScript origins"**, add:
   - `http://localhost:5000`
   - `http://127.0.0.1:5000`
4. Click **SAVE**
5. Wait 5 minutes
6. Try again in an incognito window

---

## Quick Test

After making changes:

1. **Clear browser cache:**
   - Press `Ctrl+Shift+Delete`
   - Select "Cached images and files"
   - Click "Clear data"

2. **Restart server:**
   ```bash
   python horror.py
   ```

3. **Test in incognito mode:**
   - Open incognito/private window
   - Go to: http://localhost:5000
   - Try signing in

---

## Diagnostic Tool

Use the diagnostic page to see exactly what's wrong:

```
http://localhost:5000/test-google-auth-detailed.html
```

This will show you:
- ✅ What's working
- ❌ What's broken
- 🔧 How to fix it

---

## Common Mistakes

❌ **Forgot to wait:** Google changes take 3-5 minutes to propagate  
❌ **Wrong email:** You must add the EXACT email you're signing in with  
❌ **Didn't clear cache:** Old cached data can cause issues  
❌ **Wrong port:** Make sure you're accessing http://localhost:5000

---

## Success Checklist

When working, you'll see:

1. ✅ Google Sign-In button appears
2. ✅ Popup opens showing your Google accounts
3. ✅ You can click your account without errors
4. ✅ Popup closes automatically
5. ✅ You see: "Welcome, [Your Name]!"

---

## Files to Read

- `GOOGLE_AUTH_FIX_FINAL.md` - Complete troubleshooting guide
- `GOOGLE_OAUTH_FIX.md` - Detailed OAuth setup instructions
- `test-google-auth-detailed.html` - Diagnostic tool

---

## Need Help?

1. Run diagnostic tool: http://localhost:5000/test-google-auth-detailed.html
2. Open browser console (F12)
3. Look for error messages
4. Check GOOGLE_AUTH_FIX_FINAL.md for solutions

---

## Your Configuration

**Client ID:** 
```
383630092112-5vqj924hq2n44tjk1gpb3bisokfab50m.apps.googleusercontent.com
```

**Required Origins:**
```
http://localhost:5000
http://127.0.0.1:5000
```

**OAuth Consent Screen:**
https://console.cloud.google.com/apis/credentials/consent

---

## TL;DR

The fix is almost always:

1. Add your email to test users
2. Wait 5 minutes
3. Try again in incognito mode

That's it! 🎃

