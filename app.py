"""
Horror Oracle - Flask + LangChain Backend
Main application file with all API endpoints
"""
from dotenv import load_dotenv
load_dotenv()

import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from urllib.parse import quote
import sqlite3
import datetime
import random
from collections import defaultdict

# Import LangChain backend modules
from backend.config import Config
from backend.langchain_setup import langchain_setup
from backend.quiz_generator import quiz_generator
from backend.movie_knowledge import movie_rag

# Import Oracle Engine
from oracle_engine.main import start_first_quiz, evaluate_and_progress

# ----- CONFIG -----
Config.validate()

# Connect to SQLite database
db_conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
db_cursor = db_conn.cursor()

app = Flask(__name__, static_url_path="", static_folder=".")
CORS(app)

# ----- IN-MEMORY STORAGE FOR RATINGS AND REVIEWS -----
movie_ratings = defaultdict(list)
movie_reviews = defaultdict(list)
movie_stats = defaultdict(lambda: {
    "gore": 0,
    "fear": 0,
    "kills": 0
})

# Predefined horror stats for popular movies
MOVIE_HORROR_STATS = {
    "saw": {"gore": 85, "fear": 7.5, "kills": 6},
    "the conjuring": {"gore": 20, "fear": 9.0, "kills": 2},
    "halloween": {"gore": 65, "fear": 8.0, "kills": 17},
    "scream": {"gore": 70, "fear": 7.0, "kills": 7},
    "friday the 13th": {"gore": 75, "fear": 7.5, "kills": 22},
    "nightmare on elm street": {"gore": 60, "fear": 8.5, "kills": 4},
    "the exorcist": {"gore": 30, "fear": 9.5, "kills": 2},
    "it": {"gore": 55, "fear": 8.0, "kills": 8},
    "midsommar": {"gore": 70, "fear": 8.0, "kills": 9},
}

# ----- HELPER FUNCTIONS FOR USER DATA -----
def load_user_data():
    """Load user data from JSON file"""
    try:
        with open(Config.USER_DATA_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    """Save user data to JSON file"""
    with open(Config.USER_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_profile(google_id):
    """Calculate user's horror profile based on their genre searches"""
    users = load_user_data()
    
    if google_id not in users or 'genre_searches' not in users[google_id]:
        return "New Horror Fan"
    
    genre_searches = users[google_id]['genre_searches']
    
    if not genre_searches:
        return "New Horror Fan"
    
    top_genre = max(genre_searches, key=genre_searches.get)
    
    profile_map = {
        "slashers": "Slasher Fan",
        "zombies": "Zombie Enthusiast",
        "vampires": "Vampire Lover",
        "gore-fests": "Gore Hound",
        "supernatural": "Supernatural Seeker",
        "demons": "Demon Hunter",
        "psycho-killers": "Psycho Thriller Fan",
        "alien-horror": "Sci-Fi Horror Fan",
        "creature-features": "Monster Movie Buff",
        "haunted-houses": "Haunted House Explorer",
        "psychological": "Mind Bender",
        "cult-horror": "Cult Classic Connoisseur"
    }
    
    return profile_map.get(top_genre, "Horror Enthusiast")

def get_movie_details_from_apis(title):
    """Get movie details from OMDB/TMDB APIs"""
    movie_details = {
        "title": title,
        "year": None,
        "director": None,
        "poster": None,
        "plot": None,
        "rating": None,
        "genres": "Horror"
    }
    
    # Try OMDB first
    if Config.OMDB_API_KEY:
        try:
            omdb_url = f"http://www.omdbapi.com/?t={quote(title)}&apikey={Config.OMDB_API_KEY}"
            omdb_response = requests.get(omdb_url, timeout=3)
            omdb_data = omdb_response.json()
            
            if omdb_data.get("Response") == "True":
                movie_details["title"] = omdb_data.get("Title", title)
                movie_details["year"] = omdb_data.get("Year")
                movie_details["director"] = omdb_data.get("Director")
                movie_details["poster"] = omdb_data.get("Poster") if omdb_data.get("Poster") != "N/A" else None
                movie_details["plot"] = omdb_data.get("Plot")
                movie_details["rating"] = omdb_data.get("imdbRating")
                movie_details["genres"] = omdb_data.get("Genre", "Horror")
                return movie_details
        except Exception as e:
            print(f"OMDB error: {e}")
    
    # Try TMDB as fallback
    if Config.TMDB_API_KEY:
        try:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={quote(title)}"
            search_response = requests.get(search_url, timeout=3)
            search_data = search_response.json()
            
            if search_data.get("results"):
                movie = search_data["results"][0]
                movie_id = movie["id"]
                
                detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={Config.TMDB_API_KEY}&append_to_response=credits"
                detail_response = requests.get(detail_url, timeout=3)
                detail_data = detail_response.json()
                
                movie_details["title"] = detail_data.get("title", title)
                movie_details["year"] = detail_data.get("release_date", "").split("-")[0] if detail_data.get("release_date") else None
                movie_details["poster"] = f"https://image.tmdb.org/t/p/w500{detail_data['poster_path']}" if detail_data.get("poster_path") else None
                movie_details["plot"] = detail_data.get("overview")
                movie_details["rating"] = str(detail_data.get("vote_average"))
                movie_details["genres"] = ", ".join([g["name"] for g in detail_data.get("genres", [])])
                
                if detail_data.get("credits") and detail_data["credits"].get("crew"):
                    directors = [p["name"] for p in detail_data["credits"]["crew"] if p.get("job") == "Director"]
                    if directors:
                        movie_details["director"] = directors[0]
                
                return movie_details
        except Exception as e:
            print(f"TMDB error: {e}")
    
    return movie_details

def get_movie_recommendations(title):
    """Get similar movie recommendations"""
    recommendations = []
    original_title_lower = title.lower().strip()
    
    if Config.TMDB_API_KEY:
        try:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={quote(title)}"
            search_response = requests.get(search_url, timeout=3)
            search_data = search_response.json()
            
            if search_data.get("results"):
                original_movie = search_data["results"][0]
                movie_id = original_movie["id"]
                original_title = original_movie.get("title", "").lower()
                
                rec_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={Config.TMDB_API_KEY}"
                rec_response = requests.get(rec_url, timeout=3)
                rec_data = rec_response.json()
                
                for movie in rec_data.get("results", []):
                    movie_title_lower = movie.get("title", "").lower()
                    
                    if movie_title_lower == original_title or movie_title_lower == original_title_lower:
                        continue
                    
                    if len(recommendations) >= 5:
                        break
                    
                    rec = {
                        "title": movie.get("title"),
                        "year": movie.get("release_date", "").split("-")[0] if movie.get("release_date") else None,
                        "poster": f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get("poster_path") else None
                    }
                    recommendations.append(rec)
                
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    
    return recommendations

def detect_query_type(query):
    """Detect what type of horror query this is"""
    query_lower = query.lower()
    
    if any(phrase in query_lower for phrase in ['tell me more', 'more details', 'more about', 'obscure details']):
        return 'tell_me_more'
    
    if any(word in query_lower for word in ['blood', 'bloody', 'bloodiest', 'gore', 'gory', 'goriest']):
        return 'bloodiest'
    elif any(word in query_lower for word in ['weird', 'bizarre', 'strange', 'crazy', 'kill', 'death']):
        return 'weird_kills'
    elif any(word in query_lower for word in ['nude', 'nudity', 'naked', 'sex']):
        return 'nudity'
    elif any(word in query_lower for word in ['zombie', 'undead', 'walking dead']):
        return 'zombies'
    elif any(word in query_lower for word in ['vampire', 'dracula', 'bloodsucker']):
        return 'vampires'
    elif any(word in query_lower for word in ['slasher', 'killer', 'masked']):
        return 'slashers'
    else:
        if len(query_lower.split()) <= 5:
            return 'specific_movie'
        return 'general'

# ----- ROUTES -----

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# ===== LANGCHAIN-POWERED ENDPOINTS =====

@app.route("/ask-oracle", methods=["POST"])
def ask_oracle():
    """Main endpoint using LangChain RAG for responses"""
    try:
        data = request.json
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        print(f"🔍 Query: {query}")
        
        query_type = detect_query_type(query)
        print(f"Query type: {query_type}")
        
        movie_details = None
        recommendations = []
        
        # Handle specific movie queries
        if query_type == 'specific_movie':
            movie_details = get_movie_details_from_apis(query)
            
            if movie_details and movie_details.get("title"):
                recommendations = get_movie_recommendations(query)
                
                # Use LangChain RAG for response
                response = movie_rag.answer_query(
                    f"Tell me about {query}",
                    query_type='specific_movie',
                    movie_context=movie_details
                )
            else:
                response = movie_rag.answer_query(query, query_type)
        
        # Handle "tell me more" queries
        elif query_type == 'tell_me_more':
            # Try to extract movie name from query
            movie_title = None
            common_movies = ['saw', 'halloween', 'scream', 'the conjuring', 'the exorcist']
            for movie in common_movies:
                if movie in query.lower():
                    movie_title = movie.title()
                    break
            
            if movie_title:
                movie_details = get_movie_details_from_apis(movie_title)
                response = movie_rag.answer_query(
                    query,
                    query_type='tell_me_more',
                    movie_context=movie_details
                )
                if movie_details:
                    recommendations = get_movie_recommendations(movie_title)
            else:
                response = movie_rag.answer_query(query, 'general')
        
        # Handle other query types with RAG
        else:
            response = movie_rag.answer_query(query, query_type)
        
        return jsonify({
            "response": response,
            "movie_details": movie_details,
            "recommendations": recommendations,
            "query_type": query_type
        })
        
    except Exception as e:
        print(f"Error in ask-oracle: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate-adaptive-quiz", methods=["POST"])
def generate_adaptive_quiz():
    """Generate AI-adaptive quiz using LangChain"""
    try:
        data = request.json
        google_id = data.get('googleId')
        quiz_number = data.get('quizNumber', 1)
        movie_title = data.get('movieTitle')
        
        # Load user's horror DNA
        users = load_user_data()
        horror_dna = {}
        
        if google_id and google_id in users:
            horror_dna = users[google_id].get('horror_dna', {
                'favorite_themes': [],
                'fear_tolerance': 50,
                'preferred_eras': [],
                'personality_traits': [],
                'quiz_history': []
            })
        else:
            # Initialize default horror DNA
            horror_dna = {
                'favorite_themes': [],
                'fear_tolerance': 50,
                'preferred_eras': [],
                'personality_traits': [],
                'quiz_history': []
            }
        
        # Generate quiz using LangChain
        quiz_result = quiz_generator.generate_adaptive_quiz(
            horror_dna=horror_dna,
            quiz_number=quiz_number,
            movie_title=movie_title
        )
        
        return jsonify(quiz_result)
        
    except Exception as e:
        print(f"Error generating adaptive quiz: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/save-quiz-results", methods=["POST"])
def save_quiz_results():
    """Save quiz results and update horror DNA"""
    try:
        data = request.json
        google_id = data.get('googleId')
        quiz_results = data.get('quizResults', {})
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        users = load_user_data()
        
        # Initialize user if not exists
        if google_id not in users:
            users[google_id] = {
                "myList": [],
                "ratings": {},
                "history": [],
                "genre_searches": {},
                "horror_profile": "New Horror Fan",
                "horror_dna": {
                    "favorite_themes": [],
                    "fear_tolerance": 50,
                    "preferred_eras": [],
                    "personality_traits": [],
                    "quiz_history": []
                }
            }
        
        if "horror_dna" not in users[google_id]:
            users[google_id]["horror_dna"] = {
                "favorite_themes": [],
                "fear_tolerance": 50,
                "preferred_eras": [],
                "personality_traits": [],
                "quiz_history": []
            }
        
        horror_dna = users[google_id]["horror_dna"]
        
        # Add quiz to history
        quiz_entry = {
            "quiz_number": len(horror_dna["quiz_history"]) + 1,
            "score": quiz_results.get('score', 0),
            "total": quiz_results.get('total', 5),
            "theme": quiz_results.get('theme', 'General'),
            "answers": quiz_results.get('answers', []),
            "timestamp": datetime.datetime.now().isoformat()
        }
        horror_dna["quiz_history"].append(quiz_entry)
        
        # Update fear tolerance
        score_percent = (quiz_results.get('score', 0) / quiz_results.get('total', 5)) * 100
        current_tolerance = horror_dna.get("fear_tolerance", 50)
        new_tolerance = min(100, current_tolerance + (score_percent / 20))
        horror_dna["fear_tolerance"] = new_tolerance
        
        save_user_data(users)
        
        # Generate immersive message using quiz generator
        next_quiz_num = len(horror_dna["quiz_history"]) + 1
        immersive_msg = quiz_generator._generate_immersive_message(next_quiz_num, new_tolerance)
        
        return jsonify({
            "success": True,
            "horror_dna": horror_dna,
            "next_quiz_number": next_quiz_num,
            "immersive_message": immersive_msg
        })
        
    except Exception as e:
        print(f"Error saving quiz results: {e}")
        return jsonify({"error": str(e)}), 500

# ===== ORACLE ENGINE QUIZ ENDPOINTS =====

@app.route("/api/start_quiz", methods=["POST"])
def api_start_quiz():
    """Starts the first quiz for a given user and returns JSON."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "guest")
    quiz = start_first_quiz(user_id)
    return jsonify(quiz)

@app.route("/api/submit_answers", methods=["POST"])
def api_submit_answers():
    """Evaluates user answers and returns score + next-step info."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "guest")
    quiz = data.get("quiz", {})
    answers = data.get("answers", {})
    result = evaluate_and_progress(user_id, quiz, answers)
    return jsonify(result)

# ===== USER DATA ENDPOINTS =====

@app.route("/track-genre-preference", methods=["POST"])
def track_genre_preference():
    """Track genre preferences"""
    try:
        data = request.json
        google_id = data.get('googleId')
        genre = data.get('genre')
        
        if not google_id or not genre:
            return jsonify({"error": "Missing googleId or genre"}), 400
        
        users = load_user_data()
        
        if google_id not in users:
            users[google_id] = {
                "myList": [],
                "ratings": {},
                "history": [],
                "genre_searches": {},
                "horror_profile": "New Horror Fan"
            }
        
        if "genre_searches" not in users[google_id]:
            users[google_id]["genre_searches"] = {}
        
        genre_lower = genre.lower()
        if genre_lower not in users[google_id]["genre_searches"]:
            users[google_id]["genre_searches"][genre_lower] = 0
        users[google_id]["genre_searches"][genre_lower] += 1
        
        users[google_id]["horror_profile"] = get_user_profile(google_id)
        
        save_user_data(users)
        
        return jsonify({
            "success": True,
            "genre_searches": users[google_id]["genre_searches"],
            "horror_profile": users[google_id]["horror_profile"]
        })
        
    except Exception as e:
        print(f"Error tracking genre preference: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-horror-profile", methods=["POST"])
def get_horror_profile_route():
    """Get user's horror profile"""
    try:
        google_id = request.json.get('googleId')
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        profile = get_user_profile(google_id)
        
        users = load_user_data()
        genre_searches = {}
        if google_id in users and "genre_searches" in users[google_id]:
            genre_searches = users[google_id]["genre_searches"]
        
        return jsonify({
            "horror_profile": profile,
            "genre_searches": genre_searches
        })
        
    except Exception as e:
        print(f"Error getting horror profile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-personalized-recommendations", methods=["POST"])
def get_personalized_recommendations():
    """Get personalized recommendations"""
    try:
        google_id = request.json.get('googleId')
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        users = load_user_data()
        
        if google_id not in users or "genre_searches" not in users[google_id]:
            return jsonify({"recommendations": []})
        
        genre_searches = users[google_id]["genre_searches"]
        
        if not genre_searches:
            return jsonify({"recommendations": []})
        
        top_genre = max(genre_searches, key=genre_searches.get)
        
        # Genre-specific recommendations
        genre_recs = {
            "slashers": ["Halloween", "Scream", "Friday the 13th"],
            "zombies": ["28 Days Later", "Train to Busan", "Dawn of the Dead"],
            "vampires": ["Let the Right One In", "30 Days of Night", "The Lost Boys"],
        }
        
        recommendations = genre_recs.get(top_genre, ["The Exorcist", "The Shining", "The Conjuring"])
        
        rec_details = []
        for movie_title in recommendations[:5]:
            details = get_movie_details_from_apis(movie_title)
            if details:
                rec_details.append(details)
        
        return jsonify({
            "recommendations": rec_details,
            "based_on_genre": top_genre,
            "horror_profile": get_user_profile(google_id)
        })
        
    except Exception as e:
        print(f"Error getting personalized recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/save-to-list", methods=["POST"])
def save_to_list():
    """Save movie to user's list"""
    data = request.json
    google_id = data.get('googleId')
    movie = data.get('movie')
    
    users = load_user_data()
    
    if google_id not in users:
        users[google_id] = {"myList": [], "ratings": {}}
    
    if movie not in users[google_id]["myList"]:
        users[google_id]["myList"].append(movie)
    
    save_user_data(users)
    
    return jsonify({"success": True, "list": users[google_id]["myList"]})

@app.route("/get-user-data", methods=["POST"])
def get_user_data():
    """Get user data"""
    google_id = request.json.get('googleId')
    
    users = load_user_data()
    if google_id in users:
        return jsonify(users[google_id])
    
    return jsonify({"myList": [], "ratings": {}})

# ===== ADDITIONAL ENDPOINTS =====

@app.route("/theater-releases", methods=["GET"])
def theater_releases():
    """Get current horror movies in theaters"""
    if not Config.TMDB_API_KEY:
        return jsonify({"releases": []})
    
    try:
        today = datetime.datetime.now()
        four_weeks_ago = today - datetime.timedelta(days=28)
        
        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": Config.TMDB_API_KEY,
            "with_genres": "27",
            "primary_release_date.gte": four_weeks_ago.strftime("%Y-%m-%d"),
            "primary_release_date.lte": today.strftime("%Y-%m-%d"),
            "sort_by": "popularity.desc",
            "page": 1,
            "region": "US"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        releases = []
        for movie in data.get("results", [])[:3]:
            releases.append({
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "poster_path": movie.get("poster_path"),
                "vote_average": movie.get("vote_average", 0)
            })
        
        return jsonify({"releases": releases})
        
    except Exception as e:
        print(f"Error getting theater releases: {e}")
        return jsonify({"releases": []})

@app.route("/get-trailer", methods=["GET"])
def get_trailer():
    """Get YouTube trailer URL"""
    try:
        movie_title = request.args.get("title", "").strip()
        
        if not movie_title or not Config.TMDB_API_KEY:
            return jsonify({"error": "Missing title or TMDB API key"}), 400
        
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={quote(movie_title)}"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        if not search_data.get("results"):
            return jsonify({"error": "Movie not found"}), 404
        
        movie_id = search_data["results"][0]["id"]
        
        videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={Config.TMDB_API_KEY}"
        videos_response = requests.get(videos_url)
        videos_data = videos_response.json()
        
        for video in videos_data.get("results", []):
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                youtube_url = f"https://www.youtube.com/watch?v={video['key']}"
                return jsonify({"trailer_url": youtube_url})
        
        return jsonify({"error": "No trailer found"}), 404
        
    except Exception as e:
        print(f"Trailer error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/random-genre/<genre>", methods=["GET"])
def random_genre(genre):
    """Get random movie from genre"""
    genre_movies = {
        "slashers": ["Halloween", "Friday the 13th", "A Nightmare on Elm Street", "Scream"],
        "zombies": ["Dawn of the Dead", "28 Days Later", "Train to Busan"],
        "vampires": ["Let the Right One In", "30 Days of Night", "The Lost Boys"]
    }
    
    movies = genre_movies.get(genre.lower(), ["The Exorcist"])
    selected_movie = random.choice(movies)
    
    movie_details = get_movie_details_from_apis(selected_movie)
    recommendations = get_movie_recommendations(selected_movie) if movie_details else []
    
    response_text = f"{genre.upper()} PICK: {selected_movie}! A horror classic you need to watch."
    
    return jsonify({
        "response": response_text,
        "movie_details": movie_details,
        "recommendations": recommendations,
        "query_type": "genre_selection",
        "genre": genre
    })

@app.route("/get-movie-stats", methods=["GET"])
def get_movie_stats():
    """Get movie stats"""
    try:
        movie_title = request.args.get("movie_title", "").lower()
        
        if not movie_title:
            return jsonify({"error": "Movie title required"}), 400
        
        ratings_list = movie_ratings.get(movie_title, [])
        avg_rating = sum(ratings_list) / len(ratings_list) if ratings_list else 0
        
        reviews_list = movie_reviews.get(movie_title, [])
        
        stats = MOVIE_HORROR_STATS.get(movie_title, {
            "gore": random.randint(20, 95),
            "fear": round(random.uniform(5.0, 10.0), 1),
            "kills": random.randint(1, 25)
        })
        
        return jsonify({
            "rating": {"average": round(avg_rating, 1), "count": len(ratings_list)},
            "reviews": reviews_list[-5:],
            "stats": stats
        })
        
    except Exception as e:
        print(f"Error getting movie stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the static directory"""
    return send_from_directory('static', filename)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🩸 HORROR ORACLE + LANGCHAIN AWAKENING... 🩸")
    print("="*50)
    print(f"📊 Server running on http://localhost:{Config.FLASK_PORT}")
    print(f"🧠 OpenAI: {'CONNECTED' if Config.OPENAI_API_KEY else 'MISSING'}")
    print(f"📦 Pinecone: {'CONNECTED' if Config.PINECONE_API_KEY else 'DISCONNECTED'}")
    print(f"🎥 TMDB API: {'CONNECTED' if Config.TMDB_API_KEY else 'MISSING'}")
    print(f"🎬 OMDB API: {'CONNECTED' if Config.OMDB_API_KEY else 'MISSING'}")
    print("="*50)
    print("🔗 LangChain Features:")
    print("   ✅ Adaptive Quiz Generation")
    print("   ✅ RAG-powered Movie Knowledge")
    print("   ✅ Intelligent Tell Me More")
    print("="*50 + "\n")
    
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)


