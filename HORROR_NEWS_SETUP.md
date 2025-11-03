# Horror News Feature Setup Guide

## Overview
The Horror News feature displays the latest horror movie news, including:
- New movie announcements
- Trailers and teasers
- Remakes and reboots
- Franchise updates
- Production news (directors, cast)
- Streaming releases
- Festival premieres
- Unusual items and general horror news

## Features
- ✅ **Smart Caching**: News is cached for 1 hour to reduce API calls
- ✅ **Category Organization**: News is automatically categorized for easy browsing
- ✅ **Horror-Themed UI**: Beautiful dark theme matching your Horror Oracle design
- ✅ **Multiple Sources**: Fetches from NewsAPI with curated fallback content
- ✅ **Refresh Button**: Manually refresh to get the latest news anytime

## Setup Instructions

### Option 1: Use with NewsAPI (Recommended for Live News)

1. **Get a Free API Key**
   - Visit: https://newsapi.org
   - Sign up for a free account
   - Copy your API key

2. **Configure the API Key**
   - Open `script-js-combined.js`
   - Find line 1636: `const NEWS_API_KEY = 'YOUR_NEWSAPI_KEY_HERE';`
   - Replace `YOUR_NEWSAPI_KEY_HERE` with your actual API key
   - Example: `const NEWS_API_KEY = 'abc123def456ghi789jkl';`

3. **Save and Test**
   - Save the file
   - Refresh your Horror Oracle page
   - Click the "Horror News" button
   - You should now see live horror news!

### Option 2: Use Curated News (No Setup Required)

If you don't configure an API key, the feature will automatically display curated horror news content from known sources like:
- Bloody Disgusting
- Dread Central
- Fangoria
- Variety
- Hollywood Reporter
- Entertainment Weekly
- Collider

This is perfect for testing or if you prefer hand-picked content!

## How to Use

1. **Access Horror News**
   - Click the "Horror News" button at the top of the page
   - A modal will open with the latest news

2. **Browse Categories**
   - News is organized by category:
     - 🎬 New Release
     - 📽️ Trailer
     - 🔄 Remake/Reboot
     - 🎞️ Franchise
     - 🎭 Production
     - 📺 Streaming
     - 🏆 Festival
     - 📰 General

3. **Read Full Articles**
   - Click on any news item to open the full article in a new tab

4. **Refresh News**
   - Click the "🔄 Refresh News" button at the bottom
   - This clears the cache and fetches fresh content

## Cache Information

- **Cache Duration**: 1 hour
- **Storage**: Browser localStorage
- **Cache Key**: `horrorNewsCache`
- **Automatic Expiry**: Cache automatically clears after 1 hour

## Search Keywords

The feature searches for news using these horror-related keywords:
- horror movie
- horror film
- scary movie
- horror remake
- horror sequel
- horror franchise
- horror director
- slasher film
- zombie movie
- supernatural horror
- horror streaming

## Troubleshooting

### News Won't Load
1. Check your internet connection
2. Verify your API key is correct (if using NewsAPI)
3. Check browser console for errors (F12)
4. Try clearing cache and refreshing

### NewsAPI Errors
- **401 Unauthorized**: Check your API key is correct
- **429 Too Many Requests**: You've hit the rate limit (free tier: 100 requests/day)
- **426 Upgrade Required**: Old endpoint, API key may need renewal

### Cache Issues
- To manually clear cache, open browser console (F12) and run:
  ```javascript
  localStorage.removeItem('horrorNewsCache');
  ```

## API Rate Limits (NewsAPI Free Tier)

- **Requests**: 100 requests per day
- **Articles**: Up to 100 articles per request
- **Updates**: Every 15 minutes for top headlines
- **History**: Up to 1 month back

With 1-hour caching, you'll use ~24 API calls per day if news is checked hourly.

## Customization

### Adjust Cache Duration
In `script-js-combined.js`, line 1633:
```javascript
const HORROR_NEWS_CACHE_DURATION = 60 * 60 * 1000; // 1 hour
```

Change to:
- 30 minutes: `30 * 60 * 1000`
- 2 hours: `2 * 60 * 60 * 1000`
- 24 hours: `24 * 60 * 60 * 1000`

### Add More Keywords
In the `fetchHorrorNews()` function, add keywords to the `horrorKeywords` array:
```javascript
const horrorKeywords = [
    'horror movie',
    'horror film',
    'YOUR_KEYWORD_HERE',  // Add here
    // ...
];
```

### Modify Curated News
Edit the `getCuratedHorrorNews()` function to add/modify fallback news items.

## Privacy & Data

- News articles are fetched from NewsAPI (if configured)
- Cache is stored locally in your browser
- No personal data is collected or transmitted
- Article sources include: Bloody Disgusting, Fangoria, Dread Central, and more

## Future Enhancements

Possible improvements:
- RSS feed integration for horror news sites
- User preferences for favorite sources
- Email notifications for major news
- Social sharing features
- Comment system

---

**Enjoy staying updated with the latest horror news! 🩸💀🎬**

