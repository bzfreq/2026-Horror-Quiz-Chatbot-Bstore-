# 🩸 Horror Oracle - Setup Instructions

## Quick Start Guide

Follow these steps to set up and run the Horror Oracle backend with Flask + LangChain.

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask and Flask-CORS
- LangChain and LangChain-OpenAI
- OpenAI SDK
- Pinecone (optional)
- All other required packages

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# Copy and paste this into a new file called .env

# REQUIRED - Get from https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here

# OPTIONAL - Get from https://www.themoviedb.org/settings/api
TMDB_API_KEY=your_tmdb_api_key_here

# OPTIONAL - Get from https://www.pinecone.io/
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp

# OPTIONAL - Get from http://www.omdbapi.com/
OMDB_API_KEY=your_omdb_api_key_here
```

**Important**: 
- The `OPENAI_API_KEY` is **required** for the LangChain features to work
- TMDB, Pinecone, and OMDB are optional but recommended
- Never commit the `.env` file to git

### Step 3: Run the Backend Server

```bash
python app.py
```

You should see:

```
==================================================
🩸 HORROR ORACLE + LANGCHAIN AWAKENING... 🩸
==================================================
📊 Server running on http://localhost:5000
🧠 OpenAI: CONNECTED
📦 Pinecone: CONNECTED
🎥 TMDB API: CONNECTED
==================================================
🔗 LangChain Features:
   ✅ Adaptive Quiz Generation
   ✅ RAG-powered Movie Knowledge
   ✅ Intelligent Tell Me More
==================================================
```

### Step 4: Open the Frontend

Open your web browser and go to:

```
http://localhost:5000
```

The frontend (`index.html`) will automatically load and connect to the backend.

## 🧪 Testing the Features

### Test 1: AI-Adaptive Quiz

1. Click the **"Face Your Nightmares"** button
2. Go through the intro screens
3. Answer the 5 AI-generated questions
4. See your Horror DNA update

### Test 2: Movie Search

1. Type a horror movie name (e.g., "The Exorcist")
2. The AI will provide intelligent information using RAG
3. Click "Tell Me More" to get progressive details
4. See movie posters and recommendations

### Test 3: Genre Selection

1. Click on any genre tag (e.g., "🔪 SLASHERS")
2. Get a random movie from that genre
3. See AI-generated description

## 📁 Project File Overview

| File | Purpose |
|------|---------|
| `app.py` | **Main Flask application** - Run this! |
| `backend/config.py` | Configuration management |
| `backend/langchain_setup.py` | LangChain initialization |
| `backend/quiz_generator.py` | AI quiz generation logic |
| `backend/movie_knowledge.py` | RAG system for movie Q&A |
| `index.html` | Frontend (pre-built, don't modify) |
| `script-js-combined.js` | Frontend JS (pre-built, don't modify) |
| `requirements.txt` | Python dependencies |
| `.env` | Your API keys (create this) |
| `user_data.json` | User quiz history and preferences |
| `horror_movies.db` | SQLite database |

## ⚙️ How It Works

### 1. Quiz Generation Flow

```
User clicks "Face Your Nightmares"
         ↓
Frontend calls /generate-adaptive-quiz
         ↓
backend/quiz_generator.py
         ↓
LangChain creates personalized quiz
         ↓
Returns 5 questions to frontend
         ↓
User answers questions
         ↓
Frontend calls /save-quiz-results
         ↓
Horror DNA updated in user_data.json
```

### 2. Movie Knowledge Flow

```
User searches "The Exorcist"
         ↓
Frontend calls /ask-oracle
         ↓
backend/movie_knowledge.py
         ↓
RAG system searches vector database
         ↓
LangChain generates response
         ↓
Movie details from TMDB/OMDB
         ↓
Returns to frontend with posters
```

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Make sure you installed all dependencies
pip install -r requirements.txt
```

### "OpenAI API key not set"

1. Check that `.env` file exists in the project root
2. Verify `OPENAI_API_KEY=your_key` is in the file
3. Restart the Flask server: `Ctrl+C` then `python app.py`

### Frontend not loading

1. Make sure the server is running (`python app.py`)
2. Go to `http://localhost:5000` (not `file://...`)
3. Check browser console for errors (F12)

### Quiz generation fails

- The system will automatically fall back to curated questions
- Check that your OpenAI API key is valid
- Check API usage limits on OpenAI dashboard

### No movie posters showing

- Add `TMDB_API_KEY` to your `.env` file
- Get a free API key from https://www.themoviedb.org/

## 🎯 Feature Highlights

### ✅ What's Working

- ✅ AI-powered adaptive quiz generation
- ✅ Retrieval-Augmented Generation for movie knowledge
- ✅ User profile tracking (Horror DNA)
- ✅ Progressive "Tell Me More" feature
- ✅ Movie recommendations with posters
- ✅ Genre-based movie selection
- ✅ Theater releases section
- ✅ Google Sign-In integration
- ✅ User watch lists and ratings

### 🎨 Frontend Features (Pre-Built)

- ✅ Cinematic intro slideshow for quizzes
- ✅ Horror-themed UI with blood effects
- ✅ Responsive design
- ✅ Real-time chat interface
- ✅ Movie poster displays
- ✅ Trailer integration

## 📚 Next Steps

1. **Get API Keys**: Sign up for free API keys from:
   - OpenAI: https://platform.openai.com/
   - TMDB: https://www.themoviedb.org/
   - Pinecone: https://www.pinecone.io/ (optional)

2. **Customize Quizzes**: Edit `backend/quiz_generator.py` to add custom question types

3. **Add Movie Data**: Populate Pinecone vector database with horror movie knowledge

4. **Deploy**: Follow `README_BACKEND.md` for production deployment

## 🆘 Need Help?

- Check `README_BACKEND.md` for detailed API documentation
- Review Flask logs in the terminal for error messages
- Browser console (F12) shows frontend errors
- Make sure all dependencies are installed

## 🚀 You're All Set!

The Horror Oracle backend is now running with:
- Flask web server
- LangChain AI integration
- Adaptive quiz system
- RAG-powered movie knowledge
- User profiling and tracking

**Happy Horror Quizzing!** 🩸🎬👻


