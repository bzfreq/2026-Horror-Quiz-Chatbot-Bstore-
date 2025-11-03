"""
Reward Node (Reward Generator)
Generates rewards and unlocks content based on user performance.
"""
import json
from typing import Dict, Optional

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


class RewardNode:
    """
    Generates rewards, achievements, and unlocks new content based on performance.
    Uses LangChain and the Horror Oracle's Reward Generator prompt.
    """
    
    def __init__(self):
        """Initialize the Reward node with LangChain components."""
        self.prompt_template = None
        self.llm = None
        self.openai_client = None
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM for reward generation."""
        try:
            Config.validate()
            
            # Try LangChain first
            if Config.OPENAI_API_KEY and LANGCHAIN_AVAILABLE and ChatOpenAI:
                try:
                    self.llm = ChatOpenAI(
                        model=Config.LLM_MODEL,
                        temperature=0.8,  # Higher temperature for creative rewards
                        max_tokens=1500,  # More tokens for detailed reward descriptions
                        api_key=Config.OPENAI_API_KEY
                    )
                    print("[OK] Reward Node: LLM initialized with LangChain")
                except Exception as e:
                    print(f"[WARN] LangChain init failed: {e}")
                    self.llm = None
            
            # Fallback to direct OpenAI client
            if not self.llm and Config.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    print("[OK] Reward Node: Using direct OpenAI client (fallback)")
                except Exception as e:
                    print(f"[WARN] OpenAI client init failed: {e}")
                    self.openai_client = None
            else:
                self.openai_client = None
                
        except Exception as e:
            print(f"[WARN] Reward Node initialization warning: {e}")
            self.openai_client = None
    
    def load_prompt(self):
        """Load the reward generator prompt template."""
        self.prompt_template = load_prompt("reward_generator_prompt")
        return self.prompt_template
    
    def generate_rewards(self, performance: dict, user_profile: dict) -> dict:
        """
        Generate rewards based on quiz performance.
        
        Args:
            performance: Dictionary with score, accuracy, and other metrics
            user_profile: User's current profile and history
            
        Returns:
            Dictionary containing:
                - rewards: Dictionary with relics, lore_fragments, achievements, progression_unlocks
                - reward_message: Oracle's speech and atmospheric description
                - profile_updates: Stat changes
                - summary: Summary of rewards earned
        """
        score = performance.get("score", 0)
        total = performance.get("out_of", 1)
        accuracy = performance.get("accuracy", 0.0)
        grade = performance.get("grade", "C")
        
        # Get Oracle's emotional state from user_profile if available
        oracle_emotion = user_profile.get("oracle_emotion", "neutral")
        oracle_tone = user_profile.get("oracle_tone", "creepy")
        
        # Generate rewards with LLM or use fallback
        if self.llm or self.openai_client:
            return self._generate_llm_rewards(
                performance, user_profile, accuracy, oracle_emotion, oracle_tone
            )
        else:
            return self._fallback_rewards(performance, user_profile, accuracy)
    
    def _generate_llm_rewards(
        self, 
        performance: dict, 
        user_profile: dict, 
        accuracy: float,
        oracle_emotion: str,
        oracle_tone: str
    ) -> dict:
        """Generate rewards using LangChain and CryReward prompt."""
        try:
            # Load prompt if not already loaded
            if not self.prompt_template:
                self.load_prompt()
            
            # Prepare context data
            context_data = {
                "accuracy": accuracy,
                "tone": oracle_tone,
                "emotion": oracle_emotion,
                "player_profile": json.dumps(user_profile, indent=2),
                "score": performance.get("score", 0),
                "total": performance.get("out_of", 1),
                "grade": performance.get("grade", "C")
            }
            
            # Build the prompt with context
            formatted_prompt = self.prompt_template
            formatted_prompt += f"\n\n=== PERFORMANCE DATA ===\n"
            formatted_prompt += f"Accuracy: {accuracy:.2%}\n"
            formatted_prompt += f"Score: {performance.get('score', 0)}/{performance.get('out_of', 1)}\n"
            formatted_prompt += f"Grade: {performance.get('grade', 'C')}\n"
            formatted_prompt += f"Oracle Tone: {oracle_tone}\n"
            formatted_prompt += f"Oracle Emotion: {oracle_emotion}\n"
            formatted_prompt += f"\n=== PLAYER PROFILE ===\n{json.dumps(user_profile, indent=2)}\n"
            formatted_prompt += f"\n\nGenerate rewards based on this performance and Oracle's emotional state. Return ONLY valid JSON."
            
            # Try LangChain method first
            if self.llm:
                chat_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are the Horror Oracle's Reward Keeper. Return ONLY valid JSON with no markdown formatting."),
                    ("user", formatted_prompt)
                ])
                
                parser = JsonOutputParser()
                chain = chat_prompt | self.llm | parser
                
                print("[REWARD NODE] Calling LLM via LangChain to generate rewards...")
                result = chain.invoke(context_data)
                
            # Fallback to direct OpenAI
            elif self.openai_client:
                print("[REWARD NODE] Calling OpenAI API directly...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are the Horror Oracle's Reward Keeper. Return ONLY valid JSON with no markdown formatting."},
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
            
            # Validate result
            if isinstance(result, dict) and "rewards" in result:
                print(f"[OK] Generated rewards via LLM | Accuracy: {accuracy:.1%}")
                return result
            else:
                print(f"[WARN] Unexpected reward format, using fallback")
                return self._fallback_rewards(performance, user_profile, accuracy)
        
        except Exception as e:
            print(f"[ERROR] Error generating rewards: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_rewards(performance, user_profile, accuracy)
    
    def _fallback_rewards(self, performance: dict, user_profile: dict, accuracy: float) -> dict:
        """Fallback rewards when LLM is unavailable."""
        score = performance.get("score", 0)
        total = performance.get("out_of", 1)
        
        # Simple fallback reward logic
        rewards_dict = {
            "relics": [],
            "lore_fragments": [],
            "achievements": [],
            "progression_unlocks": []
        }
        
        if accuracy == 1.0:  # Perfect score
            rewards_dict["relics"] = [{
                "id": "perfect_knowledge_crystal",
                "name": "Perfect Knowledge Crystal",
                "description": "A crystalline shard that glows with the light of perfect understanding.",
                "rarity": "legendary",
                "type": "artifact"
            }]
            rewards_dict["achievements"] = [{
                "id": "flawless_horror_scholar",
                "name": "Flawless Horror Scholar",
                "description": "Achieved perfect score on a horror quiz",
                "rarity": "gold"
            }]
        
        return {
            "rewards": rewards_dict,
            "reward_message": {
                "oracle_speech": f"You scored {score}/{total}. The Oracle acknowledges your effort.",
                "tone": "neutral",
                "atmospheric_description": "The chamber awaits your next move."
            },
            "profile_updates": {
                "bravery": 2 if accuracy >= 0.7 else 0,
                "lore_knowledge": 3 if accuracy >= 0.8 else 1
            },
            "summary": {
                "total_relics_earned": len(rewards_dict["relics"]),
                "total_lore_fragments_earned": 0,
                "total_achievements_earned": len(rewards_dict["achievements"]),
                "rarity_breakdown": {"common": 0, "uncommon": 0, "rare": 0, "legendary": 0, "cursed": 0}
            }
        }
    
    def check_achievements(self, user_profile: dict) -> list:
        """
        Check if user has earned any new achievements.
        
        Args:
            user_profile: User's complete profile
            
        Returns:
            List of newly earned achievements
        """
        # TODO: Implement achievement checking logic
        return []
    
    def unlock_content(self, unlock_type: str, user_profile: dict) -> dict:
        """
        Unlock new content for the user.
        
        Args:
            unlock_type: Type of content to unlock
            user_profile: User's profile
            
        Returns:
            Dictionary with unlocked content details
        """
        # TODO: Implement with LangChain and the prompt template
        return {
            "type": unlock_type,
            "description": "New content unlocked!",
            "content": {}
        }


def create_reward_node():
    """Factory function to create a reward node."""
    return RewardNode()

