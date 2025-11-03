"""
Configuration module for Horror Oracle backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for Horror Oracle"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OMDB_API_KEY = os.getenv("OMDB_API_KEY")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    
    # LangChain Settings
    PINECONE_INDEX_NAME = "horror-movies"
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.7
    
    # Database
    DATABASE_PATH = "horror_movies.db"
    USER_DATA_PATH = "user_data.json"
    
    # Quiz Settings
    QUIZ_QUESTIONS_COUNT = 5
    QUIZ_MAX_TOKENS = 1000
    QUIZ_TEMPERATURE = 0.9
    
    # Flask Settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    FLASK_DEBUG = True
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            print(f"⚠️  WARNING: Missing required environment variables: {', '.join(missing)}")
            print("   Some features may be limited.")
        
        optional = {
            "PINECONE_API_KEY": cls.PINECONE_API_KEY,
            "OMDB_API_KEY": cls.OMDB_API_KEY,
            "TMDB_API_KEY": cls.TMDB_API_KEY,
        }
        
        for key, value in optional.items():
            if not value:
                print(f"ℹ️  Optional: {key} not set")


