"""
Recommender Node
Recommends horror movies based on user profile and quiz performance.
"""
import json
from typing import Dict, List, Optional

# Try to import LangChain dependencies (optional)
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] LangChain import failed: {e}")
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    ChatPromptTemplate = None
    JsonOutputParser = None

from oracle_engine.prompt_loader import load_prompt
from backend.config import Config


class RecommenderNode:
    """
    Generates personalized horror movie recommendations using LangChain.
    Uses LangChain and the Horror Oracle's Recommender prompt.
    """
    
    def __init__(self):
        """Initialize the Recommender node with LangChain components."""
        self.prompt_template = None
        self.llm = None
        self.openai_client = None
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM for recommendations."""
        try:
            Config.validate()
            
            # Try LangChain first
            if Config.OPENAI_API_KEY and LANGCHAIN_AVAILABLE and ChatOpenAI:
                try:
                    self.llm = ChatOpenAI(
                        model=Config.LLM_MODEL,
                        temperature=0.8,  # Higher temperature for creative recommendations
                        max_tokens=1500,  # Enough for detailed recommendations
                        api_key=Config.OPENAI_API_KEY
                    )
                    print("[OK] Recommender Node: LLM initialized with LangChain")
                except Exception as e:
                    print(f"[WARN] LangChain init failed: {e}")
                    self.llm = None
            
            # Fallback to direct OpenAI client
            if not self.llm and Config.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    print("[OK] Recommender Node: Using direct OpenAI client (fallback)")
                except Exception as e:
                    print(f"[WARN] OpenAI client init failed: {e}")
                    self.openai_client = None
            else:
                self.openai_client = None
                
        except Exception as e:
            print(f"[WARN] Recommender Node initialization warning: {e}")
            self.openai_client = None
    
    def load_prompt(self):
        """Load the recommender prompt template."""
        self.prompt_template = load_prompt("recommender_prompt")
        return self.prompt_template
    
    def recommend_movies(self, user_profile: dict, context: dict = None) -> list:
        """
        Generate personalized horror movie recommendations.
        
        Args:
            user_profile: User's preferences and history
            context: Optional context (recent_quiz_theme, performance, oracle_emotion, etc.)
            
        Returns:
            List of recommended movie dictionaries
        """
        if context is None:
            context = {}
        
        # Generate recommendations with LLM or use fallback
        if self.llm or self.openai_client:
            return self._generate_llm_recommendations(user_profile, context)
        else:
            return self._fallback_recommendations(user_profile, context)
    
    def _generate_llm_recommendations(
        self,
        user_profile: dict,
        context: dict
    ) -> list:
        """Generate recommendations using LangChain and prompt template."""
        try:
            # Load prompt if not already loaded
            if not self.prompt_template:
                self.load_prompt()
            
            # Prepare context data
            formatted_prompt = self.prompt_template
            formatted_prompt += f"\n\n=== USER PROFILE ===\n"
            formatted_prompt += f"{json.dumps(user_profile, indent=2)}\n"
            formatted_prompt += f"\n=== CONTEXT ===\n"
            formatted_prompt += f"{json.dumps(context, indent=2)}\n"
            formatted_prompt += f"\n\nGenerate personalized horror movie recommendations. Return ONLY valid JSON."
            
            # Try LangChain method first
            if self.llm:
                chat_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are the Horror Oracle's Recommender. Return ONLY valid JSON with no markdown formatting. Recommend only real, existing horror films."),
                    ("user", formatted_prompt)
                ])
                
                parser = JsonOutputParser()
                chain = chat_prompt | self.llm | parser
                
                print("[RECOMMENDER NODE] Calling LLM via LangChain to generate recommendations...")
                result = chain.invoke({
                    "user_profile": user_profile,
                    "context": context
                })
                
            # Fallback to direct OpenAI
            elif self.openai_client:
                print("[RECOMMENDER NODE] Calling OpenAI API directly...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are the Horror Oracle's Recommender. Return ONLY valid JSON with no markdown formatting. Recommend only real, existing horror films."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:].strip()
                
                result = json.loads(content)
            
            # Extract recommendations
            if isinstance(result, dict) and "recommendations" in result:
                recommendations = result.get("recommendations", [])
                print(f"[OK] Generated {len(recommendations)} recommendations via LLM")
                return recommendations
            elif isinstance(result, list):
                print(f"[OK] Generated {len(result)} recommendations via LLM (direct list)")
                return result
            else:
                print(f"[WARN] Unexpected recommendation format, using fallback")
                return self._fallback_recommendations(user_profile, context)
        
        except Exception as e:
            print(f"[ERROR] Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_recommendations(user_profile, context)
    
    def _fallback_recommendations(self, user_profile: dict, context: dict) -> list:
        """Fallback recommendations when LLM is unavailable."""
        # Basic fallback: recommend classic horror films based on preferred theme
        favorite_theme = user_profile.get("favorite_theme", "general_horror")
        
        fallback_films = {
            "slasher": [
                {"title": "Halloween", "year": 1978, "director": "John Carpenter", "subgenre": "slasher", "difficulty_level": "intermediate"},
                {"title": "Friday the 13th", "year": 1980, "director": "Sean S. Cunningham", "subgenre": "slasher", "difficulty_level": "beginner"}
            ],
            "psychological": [
                {"title": "The Shining", "year": 1980, "director": "Stanley Kubrick", "subgenre": "psychological", "difficulty_level": "advanced"},
                {"title": "Psycho", "year": 1960, "director": "Alfred Hitchcock", "subgenre": "psychological", "difficulty_level": "intermediate"}
            ],
            "supernatural": [
                {"title": "The Exorcist", "year": 1973, "director": "William Friedkin", "subgenre": "supernatural", "difficulty_level": "advanced"},
                {"title": "The Conjuring", "year": 2013, "director": "James Wan", "subgenre": "supernatural", "difficulty_level": "intermediate"}
            ]
        }
        
        recommendations = fallback_films.get(favorite_theme, [
            {"title": "The Exorcist", "year": 1973, "director": "William Friedkin", "subgenre": "general_horror", "difficulty_level": "intermediate"},
            {"title": "Halloween", "year": 1978, "director": "John Carpenter", "subgenre": "slasher", "difficulty_level": "intermediate"}
        ])
        
        # Add why_recommended and oracle_message
        for rec in recommendations:
            rec["why_recommended"] = f"Classic {rec['subgenre']} horror film matching your preferences"
            rec["oracle_message"] = f"The Oracle suggests this timeless {rec['subgenre']} masterpiece..."
        
        return recommendations
    
    def explain_recommendation(self, movie: dict, user_profile: dict) -> str:
        """
        Generate an explanation for why a movie was recommended.
        
        Args:
            movie: Movie data
            user_profile: User's profile
            
        Returns:
            Explanation text
        """
        # TODO: Implement with LangChain and the prompt template
        return "The Oracle believes this film will resonate with your fears..."
    
    def rank_movies(self, movies: list, user_profile: dict) -> list:
        """
        Rank a list of movies based on user preferences.
        
        Args:
            movies: List of movie dictionaries
            user_profile: User's profile
            
        Returns:
            Sorted list of movies with relevance scores
        """
        # TODO: Implement ranking logic with LangChain
        return movies


def create_recommender_node():
    """Factory function to create a recommender node."""
    return RecommenderNode()

