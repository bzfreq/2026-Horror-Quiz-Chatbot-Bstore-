"""
Profile Node (Profile Updater)
Updates and maintains user profiles based on quiz performance and preferences.
"""
import json
from typing import Dict, Optional
from datetime import datetime

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


class ProfileNode:
    """
    Updates user profiles with performance data and preference insights.
    Uses LangChain and the Horror Oracle's Profile Updater prompt.
    """
    
    def __init__(self):
        """Initialize the Profile node with LangChain components."""
        self.prompt_template = None
        self.llm = None
        self.openai_client = None
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM for profile updates."""
        try:
            Config.validate()
            
            # Try LangChain first
            if Config.OPENAI_API_KEY and LANGCHAIN_AVAILABLE and ChatOpenAI:
                try:
                    self.llm = ChatOpenAI(
                        model=Config.LLM_MODEL,
                        temperature=0.7,  # Moderate temperature for balanced analysis
                        max_tokens=1200,  # Enough for detailed profile updates
                        api_key=Config.OPENAI_API_KEY
                    )
                    print("[OK] Profile Node: LLM initialized with LangChain")
                except Exception as e:
                    print(f"[WARN] LangChain init failed: {e}")
                    self.llm = None
            
            # Fallback to direct OpenAI client
            if not self.llm and Config.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    print("[OK] Profile Node: Using direct OpenAI client (fallback)")
                except Exception as e:
                    print(f"[WARN] OpenAI client init failed: {e}")
                    self.openai_client = None
            else:
                self.openai_client = None
                
        except Exception as e:
            print(f"[WARN] Profile Node initialization warning: {e}")
            self.openai_client = None
    
    def load_prompt(self):
        """Load the profile updater prompt template."""
        self.prompt_template = load_prompt("profile_updater_prompt")
        return self.prompt_template
    
    def update_profile(self, user_id: str, performance_data: dict, quiz_metadata: dict) -> dict:
        """
        Update user profile with new performance data.
        
        Args:
            user_id: User identifier
            performance_data: Quiz performance metrics (score, out_of, accuracy, grade)
            quiz_metadata: Quiz difficulty, theme, tone
            
        Returns:
            Updated user profile dictionary
        """
        # Get current profile (or create default)
        current_profile = self.get_profile(user_id)
        
        # Merge current profile with defaults if needed
        if not current_profile.get("name"):
            current_profile = {
            "user_id": user_id,
                "name": user_id,
                "bravery": 50,
                "lore_knowledge": 50,
                "logic": 50,
                "fear_level": 50,
                "difficulty_level": "intermediate",
            "preferred_themes": [],
                "favorite_theme": "general_horror",
                "preferred_tone": "creepy",
                "quiz_history": [],
                "chambers_completed": 0,
                "total_questions_answered": 0,
                "perfect_quizzes": 0,
                "average_accuracy": 0.0
            }
        
        # Generate updated profile with LLM or use fallback
        if self.llm or self.openai_client:
            return self._generate_llm_profile_update(
                current_profile, performance_data, quiz_metadata, user_id
            )
        else:
            return self._fallback_profile_update(
                current_profile, performance_data, quiz_metadata
            )
    
    def _generate_llm_profile_update(
        self,
        current_profile: dict,
        performance_data: dict,
        quiz_metadata: dict,
        user_id: str = None
    ) -> dict:
        """Generate profile update using LangChain and prompt template."""
        try:
            # Load prompt if not already loaded
            if not self.prompt_template:
                self.load_prompt()
            
            # Prepare context data
            formatted_prompt = self.prompt_template
            formatted_prompt += f"\n\n=== PERFORMANCE DATA ===\n"
            formatted_prompt += f"{json.dumps(performance_data, indent=2)}\n"
            formatted_prompt += f"\n=== QUIZ METADATA ===\n"
            formatted_prompt += f"{json.dumps(quiz_metadata, indent=2)}\n"
            formatted_prompt += f"\n=== CURRENT PROFILE ===\n"
            formatted_prompt += f"{json.dumps(current_profile, indent=2)}\n"
            formatted_prompt += f"\n\nAnalyze this performance and update the profile. Return ONLY valid JSON."
            
            # Try LangChain method first
            if self.llm:
                chat_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are the Horror Oracle's Profile Keeper. Return ONLY valid JSON with no markdown formatting."),
                    ("user", formatted_prompt)
                ])
                
                parser = JsonOutputParser()
                chain = chat_prompt | self.llm | parser
                
                print("[PROFILE NODE] Calling LLM via LangChain to update profile...")
                result = chain.invoke({
                    "performance_data": performance_data,
                    "quiz_metadata": quiz_metadata,
                    "current_profile": current_profile
                })
                
            # Fallback to direct OpenAI
            elif self.openai_client:
                print("[PROFILE NODE] Calling OpenAI API directly...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are the Horror Oracle's Profile Keeper. Return ONLY valid JSON with no markdown formatting."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )
                
                content = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:].strip()
                
                result = json.loads(content)
            
            # Merge LLM updates with current profile
            updated_profile = current_profile.copy()
            
            # Apply stat changes
            if "stats_delta" in result:
                delta = result["stats_delta"]
                updated_profile["bravery"] = max(0, min(100, updated_profile.get("bravery", 50) + delta.get("bravery_change", 0)))
                updated_profile["lore_knowledge"] = max(0, min(100, updated_profile.get("lore_knowledge", 50) + delta.get("lore_knowledge_change", 0)))
                updated_profile["logic"] = max(0, min(100, updated_profile.get("logic", 50) + delta.get("logic_change", 0)))
                updated_profile["fear_level"] = max(0, min(100, updated_profile.get("fear_level", 50) + delta.get("fear_level_change", 0)))
            
            # Update difficulty and preferences
            if "difficulty_level" in result:
                updated_profile["difficulty_level"] = result["difficulty_level"]
            if "preferred_themes" in result:
                updated_profile["preferred_themes"] = result["preferred_themes"]
            if "favorite_theme" in result:
                updated_profile["favorite_theme"] = result["favorite_theme"]
            if "preferred_tone" in result:
                updated_profile["preferred_tone"] = result["preferred_tone"]
            
            # Update history
            updated_profile["chambers_completed"] = updated_profile.get("chambers_completed", 0) + 1
            updated_profile["total_questions_answered"] = updated_profile.get("total_questions_answered", 0) + performance_data.get("out_of", 0)
            
            if performance_data.get("accuracy", 0) == 1.0:
                updated_profile["perfect_quizzes"] = updated_profile.get("perfect_quizzes", 0) + 1
            
            # Update average accuracy
            current_avg = updated_profile.get("average_accuracy", 0.0)
            total_quizzes = updated_profile.get("chambers_completed", 1)
            new_accuracy = performance_data.get("accuracy", 0.0)
            updated_profile["average_accuracy"] = ((current_avg * (total_quizzes - 1)) + new_accuracy) / total_quizzes
            
            updated_profile["updated_at"] = datetime.now().isoformat()
            updated_profile["user_id"] = current_profile.get("user_id", user_id or "unknown")
            updated_profile["name"] = current_profile.get("name", user_id or current_profile.get("user_id", "unknown"))
            
            # Validate result
            if isinstance(result, dict):
                print(f"[OK] Profile updated via LLM | Difficulty: {updated_profile.get('difficulty_level')}")
                return updated_profile
            else:
                print(f"[WARN] Unexpected profile format, using fallback")
                return self._fallback_profile_update(current_profile, performance_data, quiz_metadata)
        
        except Exception as e:
            print(f"[ERROR] Error updating profile: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_profile_update(current_profile, performance_data, quiz_metadata)
    
    def _fallback_profile_update(
        self,
        current_profile: dict,
        performance_data: dict,
        quiz_metadata: dict
    ) -> dict:
        """Fallback profile update when LLM is unavailable."""
        accuracy = performance_data.get("accuracy", 0.0)
        score = performance_data.get("score", 0)
        total = performance_data.get("out_of", 1)
        
        updated = current_profile.copy()
        
        # Simple stat updates
        if accuracy >= 0.8:
            updated["bravery"] = min(100, updated.get("bravery", 50) + 3)
            updated["lore_knowledge"] = min(100, updated.get("lore_knowledge", 50) + 5)
            updated["logic"] = min(100, updated.get("logic", 50) + 2)
            updated["fear_level"] = max(0, updated.get("fear_level", 50) - 3)
        elif accuracy >= 0.6:
            updated["bravery"] = min(100, updated.get("bravery", 50) + 2)
            updated["lore_knowledge"] = min(100, updated.get("lore_knowledge", 50) + 3)
            updated["logic"] = min(100, updated.get("logic", 50) + 1)
            updated["fear_level"] = max(0, updated.get("fear_level", 50) - 1)
        elif accuracy >= 0.4:
            updated["lore_knowledge"] = min(100, updated.get("lore_knowledge", 50) + 1)
        else:
            updated["fear_level"] = min(100, updated.get("fear_level", 50) + 4)
            updated["bravery"] = max(0, updated.get("bravery", 50) - 2)
        
        # Update difficulty
        if accuracy >= 0.85:
            difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
            current_idx = difficulty_levels.index(updated.get("difficulty_level", "intermediate")) if updated.get("difficulty_level", "intermediate") in difficulty_levels else 1
            if current_idx < len(difficulty_levels) - 1:
                updated["difficulty_level"] = difficulty_levels[current_idx + 1]
        elif accuracy < 0.3:
            difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
            current_idx = difficulty_levels.index(updated.get("difficulty_level", "intermediate")) if updated.get("difficulty_level", "intermediate") in difficulty_levels else 1
            if current_idx > 0:
                updated["difficulty_level"] = difficulty_levels[current_idx - 1]
        
        # Update theme preferences
        quiz_theme = quiz_metadata.get("theme", "general_horror")
        if accuracy >= 0.7 and quiz_theme not in updated.get("preferred_themes", []):
            if "preferred_themes" not in updated:
                updated["preferred_themes"] = []
            updated["preferred_themes"].append(quiz_theme)
            if not updated.get("favorite_theme"):
                updated["favorite_theme"] = quiz_theme
        
        # Update history
        updated["chambers_completed"] = updated.get("chambers_completed", 0) + 1
        updated["total_questions_answered"] = updated.get("total_questions_answered", 0) + total
        if accuracy == 1.0:
            updated["perfect_quizzes"] = updated.get("perfect_quizzes", 0) + 1
        
        # Update average accuracy
        current_avg = updated.get("average_accuracy", 0.0)
        total_quizzes = updated.get("chambers_completed", 1)
        updated["average_accuracy"] = ((current_avg * (total_quizzes - 1)) + accuracy) / total_quizzes
        
        updated["updated_at"] = datetime.now().isoformat()
        
        return updated
    
    def analyze_preferences(self, user_history: list) -> dict:
        """
        Analyze user's horror preferences from their history.
        
        Args:
            user_history: List of past quiz results and interactions
            
        Returns:
            Dictionary with preference analysis
        """
        # TODO: Implement with LangChain and the prompt template
        return {
            "favorite_subgenres": [],
            "difficulty_comfort": "intermediate",
            "engagement_level": "medium"
        }
    
    def get_profile(self, user_id: str) -> dict:
        """
        Retrieve user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary
        """
        # TODO: Implement profile retrieval from storage
        return {
            "user_id": user_id,
            "difficulty_level": "beginner",
            "preferred_themes": []
        }


def create_profile_node():
    """Factory function to create a profile node."""
    return ProfileNode()

