# Horror Oracle - Flask + LangChain Backend

This is the backend system for Horror Oracle, a horror movie quiz web application powered by Flask and LangChain.

## 🏗️ Architecture

The backend is built with:
- **Flask**: Web framework for API endpoints
- **LangChain**: AI orchestration for quiz generation and RAG
- **OpenAI**: LLM for intelligent responses
- **Pinecone**: Vector database for semantic search (optional)
- **SQLite**: Local database for movie data
- **TMDB/OMDB APIs**: Movie information and posters

## 📁 Project Structure

```
horror-oracle/
├── app.py                      # Main Flask application (USE THIS instead of horror.py)
├── backend/
│   ├── __init__.py            # Backend module initialization
│   ├── config.py              # Configuration management
│   ├── langchain_setup.py     # LangChain components setup
│   ├── quiz_generator.py      # AI-powered quiz generator
│   └── movie_knowledge.py     # RAG system for movie Q&A
├── index.html                 # Frontend (DO NOT MODIFY)
├── script-js-combined.js      # Frontend JS (DO NOT MODIFY)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Template for environment variables
├── user_data.json            # User preferences and quiz history
└── horror_movies.db          # SQLite database
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
- `OPENAI_API_KEY`: **Required** - Get from https://platform.openai.com/
- `TMDB_API_KEY`: Recommended - Get from https://www.themoviedb.org/settings/api
- `PINECONE_API_KEY`: Optional - Get from https://www.pinecone.io/
- `OMDB_API_KEY`: Optional - Get from http://www.omdbapi.com/

### 3. Run the Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

## 🎯 Key Features

### 1. **Adaptive Quiz Generation** (`/generate-adaptive-quiz`)
- Uses LangChain to generate personalized quizzes
- Adapts difficulty based on user's "Horror DNA"
- Tracks user preferences and learning patterns
- Generates 5 questions including profile questions

### 2. **RAG-Powered Movie Knowledge** (`/ask-oracle`)
- Retrieval-Augmented Generation for accurate movie info
- Vector search for semantic similarity
- Conversational responses about horror movies
- Multi-level "Tell Me More" feature

### 3. **User Profiling System**
- Tracks genre preferences
- Builds "Horror DNA" profile
- Personalized recommendations
- Progressive difficulty adjustment

## 🔌 API Endpoints

### Quiz Endpoints

#### `POST /generate-adaptive-quiz`
Generate an AI-adaptive horror quiz.

**Request:**
```json
{
  "googleId": "user_google_id",
  "quizNumber": 1,
  "movieTitle": "The Exorcist"  // optional
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "Which horror atmosphere draws you in most?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "is_profile": true
    }
  ],
  "theme": "Supernatural Horror",
  "difficulty": "Intermediate",
  "quiz_number": 1,
  "ai_message": "The AI awakens... studying your fear patterns..."
}
```

#### `POST /save-quiz-results`
Save quiz results and update user's Horror DNA.

**Request:**
```json
{
  "googleId": "user_google_id",
  "quizResults": {
    "score": 4,
    "total": 5,
    "theme": "Supernatural Horror",
    "answers": [...],
    "profile_answers": [...]
  }
}
```

### Movie Knowledge Endpoints

#### `POST /ask-oracle`
Ask questions about horror movies using RAG.

**Request:**
```json
{
  "query": "Tell me about The Exorcist"
}
```

**Response:**
```json
{
  "response": "The Exorcist is LEGENDARY! Directed by William Friedkin...",
  "movie_details": {
    "title": "The Exorcist",
    "year": "1973",
    "director": "William Friedkin",
    "poster": "https://...",
    "plot": "...",
    "rating": "8.1"
  },
  "recommendations": [...],
  "query_type": "specific_movie"
}
```

### User Data Endpoints

#### `POST /track-genre-preference`
Track user's genre preferences for profiling.

#### `POST /get-horror-profile`
Get user's calculated horror profile.

#### `POST /get-personalized-recommendations`
Get movie recommendations based on user preferences.

## 🧠 LangChain Integration

### Quiz Generation Chain

```python
from backend.quiz_generator import quiz_generator

quiz = quiz_generator.generate_adaptive_quiz(
    horror_dna={
        'fear_tolerance': 75,
        'favorite_themes': ['supernatural', 'psychological'],
        'quiz_history': [...]
    },
    quiz_number=2
)
```

### Movie Knowledge RAG Chain

```python
from backend.movie_knowledge import movie_rag

response = movie_rag.answer_query(
    query="What makes The Shining so scary?",
    query_type="general"
)
```

## 📊 Horror DNA System

The Horror DNA system tracks:

- **Fear Tolerance** (0-100): Increases with quiz performance
- **Favorite Themes**: Extracted from profile questions and genre searches
- **Quiz History**: All past quiz results with timestamps
- **Preferred Eras**: Classic vs Modern horror preferences
- **Personality Traits**: Derived from answer patterns

## 🛠️ Development

### Adding New Quiz Question Types

Edit `backend/quiz_generator.py`:

```python
def _generate_fallback_quiz(self, horror_dna, quiz_number):
    # Add your custom question pool here
    custom_questions = [...]
```

### Extending the RAG System

Edit `backend/movie_knowledge.py`:

```python
def _fallback_response(self, query, query_type):
    # Add custom knowledge responses
```

### Adding New Movie Data Sources

Edit `app.py` - `get_movie_details_from_apis()` function.

## 🔒 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment variables for all secrets
- Validate user input on all endpoints

## 📝 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API for LangChain LLM |
| `PINECONE_API_KEY` | ❌ Optional | Vector database for RAG |
| `TMDB_API_KEY` | ❌ Optional | Movie data and posters |
| `OMDB_API_KEY` | ❌ Optional | Fallback movie API |
| `PINECONE_ENVIRONMENT` | ❌ Optional | Pinecone region |

## 🐛 Troubleshooting

### "OpenAI API key not set"
- Make sure `.env` file exists and contains `OPENAI_API_KEY=your_key`
- Restart the Flask server after adding the key

### "Pinecone initialization failed"
- Pinecone is optional - the app will work without it
- Check `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` in `.env`

### "No module named 'backend'"
- Make sure you're running `python app.py` from the project root directory

### Quiz generation errors
- Check OpenAI API key is valid
- System will fall back to curated questions if LangChain fails

## 📚 Documentation

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)

## 🎬 Frontend Integration

The frontend (`index.html` and `script-js-combined.js`) is **already configured** to work with these endpoints. No frontend changes needed.

The JavaScript makes calls to:
- `/generate-adaptive-quiz` - For quiz generation
- `/ask-oracle` - For movie queries
- `/save-quiz-results` - For saving quiz data
- Other endpoints for user data and preferences

## 🚀 Production Deployment

For production:

1. Set `FLASK_DEBUG=False` in `.env`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper CORS origins
4. Use PostgreSQL instead of SQLite for user data
5. Enable rate limiting
6. Add authentication middleware

Example with gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📄 License

This project is part of Horror Oracle - a horror movie quiz application.

---

**Built with** ❤️ **and** 🩸 **using Flask + LangChain**


