"""
Fear Meter Node
Calculates and tracks the user's "fear level" based on their choices and performance.
Translates quiz scores into the Oracle's emotional and tonal state.
"""
try:
    from oracle_engine.prompt_loader import load_prompt
except ImportError:
    # Fallback if oracle_engine dependencies aren't available
    def load_prompt(prompt_name):
        return f"Prompt template for {prompt_name}"


class FearMeterNode:
    """
    Tracks and calculates the user's fear level, providing psychological profiling
    based on their horror preferences and quiz performance.
    Translates quiz performance into Oracle's emotional state and behavior.
    """
    
    def __init__(self):
        """Initialize the Fear Meter node."""
        self.prompt_template = None
        self.tone_transitions = {
            "reverent": ["ancient", "impressed", "neutral"],
            "mocking": ["creepy", "disappointed", "amused"],
            "ancient": ["reverent", "neutral", "creepy"],
            "creepy": ["mocking", "ancient", "disappointed"],
            "impressed": ["reverent", "ancient", "neutral"],
            "disappointed": ["mocking", "creepy", "neutral"],
            "neutral": ["creepy", "ancient", "mocking"]
        }
    
    def load_prompt(self):
        """Load the fear meter prompt template."""
        self.prompt_template = load_prompt("fear_meter_prompt")
        return self.prompt_template
    
    def translate_to_oracle_state(self, accuracy: float, previous_tone: str, 
                                   player_profile: dict) -> dict:
        """
        Translate quiz performance into Oracle's emotional and tonal state.
        
        Args:
            accuracy: Quiz accuracy (0.0 - 1.0)
            previous_tone: Previous Oracle tone (creepy, mocking, ancient, reverent, etc.)
            player_profile: Player data with keys:
                - name: Player name
                - bravery: Bravery score (0-100)
                - lore_knowledge: Lore knowledge score (0-100)
                - logic: Logic score (0-100)
                - fear_level: Current fear level (0-100, optional)
                
        Returns:
            Dictionary containing Oracle state and behavior for next interaction:
                - oracle_tone: Current emotional tone
                - oracle_emotion: Specific emotion
                - intensity: Expression intensity (0-1)
                - next_tone: Suggested tone for next interaction
                - fear_shift: Change in player's fear level (-1 to 1)
                - atmospheric_message: Oracle's reaction
                - player_state: Updated player analysis
                - oracle_behavior: Behavioral modifiers
                - narrative_context: Atmospheric narrative elements
        """
        # Determine Oracle's tone based on accuracy
        if accuracy >= 0.9:
            oracle_tone = "reverent"
            oracle_emotion = "impressed"
            intensity = 0.85
            fear_shift = -0.2
            difficulty_adjustment = "reward"
            reveal_lore = True
            mock_intensity = "low"
            confidence = "confident"
            performance_trend = "improving"
            
        elif accuracy >= 0.7:
            oracle_tone = "ancient"
            oracle_emotion = "respectful"
            intensity = 0.6
            fear_shift = -0.1
            difficulty_adjustment = "maintain"
            reveal_lore = True
            mock_intensity = "low"
            confidence = "confident"
            performance_trend = "stable"
            
        elif accuracy >= 0.5:
            oracle_tone = "neutral"
            oracle_emotion = "observing"
            intensity = 0.5
            fear_shift = 0.0
            difficulty_adjustment = "maintain"
            reveal_lore = False
            mock_intensity = "medium"
            confidence = "neutral"
            performance_trend = "stable"
            
        elif accuracy >= 0.3:
            oracle_tone = "disappointed"
            oracle_emotion = "condescending"
            intensity = 0.7
            fear_shift = 0.15
            difficulty_adjustment = "maintain"
            reveal_lore = False
            mock_intensity = "medium"
            confidence = "shaken"
            performance_trend = "declining"
            
        else:  # < 0.3
            oracle_tone = "mocking"
            oracle_emotion = "amused"
            intensity = 0.9
            fear_shift = 0.3
            difficulty_adjustment = "punish"
            reveal_lore = False
            mock_intensity = "high"
            confidence = "terrified"
            performance_trend = "declining"
        
        # Calculate next tone based on transitions
        next_tone = self._get_next_tone(oracle_tone, accuracy, previous_tone)
        
        # Generate atmospheric message
        atmospheric_message = self._generate_atmospheric_message(
            oracle_tone, accuracy, player_profile.get("name", "mortal")
        )
        
        # Update player's fear level
        current_fear = player_profile.get("fear_level", 50)
        new_fear_level = max(0, min(100, current_fear + (fear_shift * 100)))
        
        # Determine chamber atmosphere
        if intensity > 0.8:
            chamber_atmosphere = "oppressive"
        elif intensity > 0.6:
            chamber_atmosphere = "tense"
        elif intensity > 0.4:
            chamber_atmosphere = "watchful"
        else:
            chamber_atmosphere = "calm"
        
        # Generate Oracle's physical stance
        oracle_stance = self._generate_oracle_stance(oracle_tone, intensity)
        
        # Generate transition text
        transition_text = self._generate_transition_text(
            oracle_tone, difficulty_adjustment, performance_trend
        )
        
        # Determine rewards
        rewards_granted = []
        if reveal_lore and accuracy >= 0.7:
            rewards_granted.append("lore_fragment")
        if accuracy >= 0.9:
            rewards_granted.append("oracle_blessing")
        
        return {
            "oracle_tone": oracle_tone,
            "oracle_emotion": oracle_emotion,
            "intensity": intensity,
            "next_tone": next_tone,
            "fear_shift": fear_shift,
            "atmospheric_message": atmospheric_message,
            "player_state": {
                "confidence": confidence,
                "performance_trend": performance_trend,
                "fear_level": int(new_fear_level)
            },
            "oracle_behavior": {
                "difficulty_adjustment": difficulty_adjustment,
                "reveal_lore": reveal_lore,
                "mock_intensity": mock_intensity,
                "rewards_granted": rewards_granted
            },
            "narrative_context": {
                "chamber_atmosphere": chamber_atmosphere,
                "oracle_stance": oracle_stance,
                "transition_text": transition_text
            }
        }
    
    def _get_next_tone(self, current_tone: str, accuracy: float, 
                       previous_tone: str) -> str:
        """Determine the next tone based on current state and transitions."""
        possible_tones = self.tone_transitions.get(current_tone, ["neutral"])
        
        # If accuracy is high, prefer positive tones
        if accuracy >= 0.8:
            positive_tones = ["reverent", "ancient", "impressed", "neutral"]
            for tone in possible_tones:
                if tone in positive_tones:
                    return tone
        
        # If accuracy is very low, prefer negative tones
        elif accuracy < 0.4:
            negative_tones = ["mocking", "disappointed", "creepy"]
            for tone in possible_tones:
                if tone in negative_tones:
                    return tone
        
        # Default to first possible tone
        return possible_tones[0] if possible_tones else "neutral"
    
    def _generate_atmospheric_message(self, tone: str, accuracy: float, 
                                      player_name: str) -> str:
        """Generate Oracle's atmospheric reaction message."""
        messages = {
            "reverent": [
                f"The Oracle bows slightly. 'Well done, {player_name}. You honor the ancient knowledge.'",
                f"'Impressive, {player_name}... The darkness acknowledges your mastery.'",
                f"The Oracle's eyes gleam with approval. 'You are worthy of the deeper mysteries.'"
            ],
            "ancient": [
                f"'You understand more than most, {player_name},' the Oracle intones solemnly.",
                f"The Oracle nods slowly. 'The old ways are not lost on you.'",
                f"'Acceptable,' whispers the ancient voice. 'Continue your journey.'"
            ],
            "neutral": [
                f"The Oracle watches {player_name} with unblinking eyes.",
                f"'Proceed,' the Oracle commands flatly.",
                f"The ancient presence observes without judgment... for now."
            ],
            "disappointed": [
                f"The Oracle sighs, a sound like wind through a crypt. 'Expected more, {player_name}.'",
                f"'Disappointing,' the Oracle mutters. 'Perhaps you are not ready.'",
                f"The Oracle's gaze darkens. '{player_name}... you stumble in the shadows.'"
            ],
            "mocking": [
                f"The Oracle's laughter echoes through the chamber. 'You stumble, {player_name}!'",
                f"'Pathetic,' the Oracle hisses with dark amusement. 'The darkness will consume you.'",
                f"The Oracle leans forward, grinning wickedly. 'Is this the best you can offer, mortal?'"
            ]
        }
        
        tone_messages = messages.get(tone, messages["neutral"])
        # Simple selection based on accuracy within tone
        index = min(len(tone_messages) - 1, int(accuracy * len(tone_messages)))
        return tone_messages[index]
    
    def _generate_oracle_stance(self, tone: str, intensity: float) -> str:
        """Generate Oracle's physical presence description."""
        stances = {
            "reverent": "The Oracle rises from its throne, robes flowing like shadow and light intertwined",
            "ancient": "The Oracle sits motionless, eyes older than time itself watching patiently",
            "neutral": "The Oracle remains still, an enigmatic presence in the darkness",
            "disappointed": "The Oracle's form seems to dim, shadows deepening around its disappointment",
            "mocking": "The Oracle leans forward, eyes gleaming with dark amusement and malice"
        }
        
        base_stance = stances.get(tone, stances["neutral"])
        
        if intensity > 0.8:
            return f"{base_stance}, power radiating from every gesture"
        elif intensity > 0.6:
            return f"{base_stance}, presence commanding attention"
        else:
            return base_stance
    
    def _generate_transition_text(self, tone: str, difficulty: str, 
                                  trend: str) -> str:
        """Generate narrative transition to next phase."""
        if difficulty == "reward" and trend == "improving":
            return "Your mastery opens new paths... The Oracle prepares deeper mysteries."
        elif difficulty == "punish" and trend == "declining":
            return "Your failure amuses the ancient one... Prepare for harsher trials."
        elif difficulty == "maintain":
            if trend == "stable":
                return "The Oracle continues to test your resolve..."
            elif trend == "improving":
                return "You show promise... but the true test lies ahead."
            else:
                return "The shadows press closer as your confidence wavers..."
        else:
            return "The Oracle's gaze follows you into the next chamber..."
    
    def calculate_fear_level(self, user_data: dict) -> dict:
        """
        Calculate the user's current fear level.
        
        Args:
            user_data: Dictionary containing:
                - quiz_history: Past quiz performance
                - genre_preferences: Preferred horror subgenres
                - scare_tolerance: How much they can handle
                - recent_answers: Most recent quiz answers
                
        Returns:
            Dictionary containing:
                - fear_score: Numerical fear level (0-100)
                - fear_category: Category (e.g., "Novice", "Veteran", "Fearless")
                - description: Narrative description of their fear profile
                - recommendations: Adjusted difficulty suggestions
        """
        # TODO: Implement with LangChain and the prompt template
        # For now, return a placeholder structure
        return {
            "fear_score": 50,
            "fear_category": "Initiate",
            "description": "You're just beginning to explore the darkness...",
            "recommendations": ["intermediate"]
        }
    
    def analyze_scare_tolerance(self, answer_history: list) -> dict:
        """
        Analyze what types of horror the user can tolerate.
        
        Args:
            answer_history: List of past answers with metadata
            
        Returns:
            Dictionary with scare tolerance analysis
        """
        # TODO: Implement with LangChain and the prompt template
        return {
            "psychological_horror": 0.5,
            "gore_tolerance": 0.5,
            "jump_scares": 0.5,
            "existential_dread": 0.5
        }
    
    def generate_fear_message(self, fear_level: int, context: str) -> str:
        """
        Generate an atmospheric message based on the user's fear level.
        
        Args:
            fear_level: Current fear score (0-100)
            context: Context for the message (e.g., "quiz_start", "level_up")
            
        Returns:
            Atmospheric message text
        """
        # TODO: Implement with LangChain and the prompt template
        if fear_level < 30:
            return "The Oracle senses your curiosity... but not yet your fear."
        elif fear_level < 70:
            return "You've glimpsed the shadows. Will you venture deeper?"
        else:
            return "The darkness recognizes you. You are one with the horror."
    
    def update_profile_with_fear_data(self, user_profile: dict, fear_data: dict) -> dict:
        """
        Update user profile with fear meter insights.
        
        Args:
            user_profile: Current user profile
            fear_data: Fear meter calculation results
            
        Returns:
            Updated user profile
        """
        # TODO: Implement profile update logic
        user_profile["fear_level"] = fear_data.get("fear_score", 50)
        user_profile["fear_category"] = fear_data.get("fear_category", "Initiate")
        return user_profile


def create_fear_meter_node():
    """Factory function to create a fear meter node."""
    return FearMeterNode()

