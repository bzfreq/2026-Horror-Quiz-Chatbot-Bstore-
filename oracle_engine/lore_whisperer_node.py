"""
Lore Whisperer Node
Generates atmospheric horror lore and backstories to enhance the quiz experience.
"""
from oracle_engine.prompt_loader import load_prompt
import random
from typing import Dict, List, Optional


class LoreWhispererNode:
    """
    Generates horror lore, backstories, and atmospheric narrative elements
    to deepen the quiz experience.
    """
    
    def __init__(self):
        """Initialize the Lore Whisperer node."""
        self.prompt_template = None
        
        # Lore fragment styles
        self.fragment_styles = [
            "cryptic_prophecy",
            "ancient_warning",
            "mocking_observation",
            "dark_wisdom",
            "eldritch_whisper"
        ]
        
        # Atmosphere presets
        self.moods = ["ominous", "dread", "eerie", "malevolent", "mysterious", "suffocating"]
        self.visual_hints_pool = [
            "flickering_candles", "shadow_figures", "blood_moon", 
            "cracked_mirrors", "writhing_shadows", "spectral_mist",
            "ancient_runes", "decaying_walls", "crimson_light"
        ]
        self.ambient_sounds = [
            "distant_whispers", "chains_rattling", "mournful_wind",
            "dripping_water", "heartbeat_echo", "screaming_silence"
        ]
    
    def load_prompt(self):
        """Load the lore whisperer prompt template."""
        self.prompt_template = load_prompt("lore_whisperer_prompt")
        return self.prompt_template
    
    def whisper_between_chambers(
        self,
        player_profile: dict,
        last_theme: str,
        emotion: str,
        performance: Optional[str] = "average"
    ) -> dict:
        """
        Generate a poetic horror fragment for transitions between quiz chambers.
        
        Args:
            player_profile: Player's traits, level, relics, etc.
            last_theme: Theme of the last quiz (e.g., "slasher", "occult")
            emotion: Oracle's current emotion from Reactor node
            performance: Player's performance (optional)
        
        Returns:
            Complete lore fragment with atmosphere, voice, and narrative hooks
        """
        # Extract player traits
        bravery = player_profile.get("bravery", 50)
        lore_knowledge = player_profile.get("lore_knowledge", 50)
        fear_level = player_profile.get("fear_level", 50)
        level = player_profile.get("level", 1)
        
        # Calculate intensity based on emotion and fear level
        intensity = self._calculate_intensity(emotion, fear_level)
        
        # Generate lore text based on emotion and context
        lore_text = self._craft_lore_text(
            emotion, 
            last_theme, 
            bravery, 
            lore_knowledge,
            performance
        )
        
        # Select fragment style
        style = self._select_fragment_style(emotion, intensity)
        
        # Build atmosphere
        atmosphere = self._build_atmosphere(emotion, intensity, last_theme)
        
        # Create oracle voice characteristics
        oracle_voice = self._define_oracle_voice(emotion, intensity)
        
        # Generate narrative hooks
        narrative_hooks = self._create_narrative_hooks(
            player_profile, 
            last_theme,
            performance
        )
        
        # Compile the complete output
        return {
            "lore_fragment": {
                "text": lore_text,
                "style": style,
                "intensity": intensity
            },
            "atmosphere": atmosphere,
            "oracle_voice": oracle_voice,
            "narrative_hooks": narrative_hooks,
            "metadata": {
                "fragment_type": "transition",
                "trigger": "quiz_completion",
                "duration_seconds": self._estimate_duration(lore_text),
                "player_level": level
            }
        }
    
    def _calculate_intensity(self, emotion: str, fear_level: float) -> float:
        """Calculate the intensity of the lore fragment."""
        emotion_intensity_map = {
            "pleased": 0.3,
            "amused": 0.5,
            "mocking": 0.7,
            "disappointed": 0.6,
            "wrathful": 0.9,
            "cruel": 0.85,
            "indifferent": 0.4
        }
        
        base_intensity = emotion_intensity_map.get(emotion, 0.5)
        fear_modifier = fear_level / 100.0
        
        # Blend emotion and fear
        intensity = (base_intensity * 0.7) + (fear_modifier * 0.3)
        return min(1.0, max(0.1, intensity))
    
    def _craft_lore_text(
        self, 
        emotion: str, 
        theme: str, 
        bravery: float,
        lore_knowledge: float,
        performance: str
    ) -> str:
        """Craft poetic lore text based on context."""
        # Define lore templates by emotion
        lore_templates = {
            "pleased": [
                f"The {theme} whispers approve... for now.",
                f"Knowledge gleams in the darkness, a rare light.",
                f"Even the shadows bow to those who know their names."
            ],
            "amused": [
                f"You dance well in this {theme} chamber, little mortal.",
                f"The Oracle chuckles—your steps intrigue the void.",
                f"Such confidence... let us see if it endures."
            ],
            "mocking": [
                f"Did you think {theme} would yield so easily?",
                f"The shadows mock your stumbling, seeker.",
                f"Knowledge slips through trembling fingers like sand."
            ],
            "disappointed": [
                f"The {theme} realm demands more than guesses.",
                f"Mediocrity echoes hollow in these chambers.",
                f"The Oracle sighs... potential squandered."
            ],
            "wrathful": [
                f"FOOL! The {theme} spirits howl at your ignorance!",
                f"Your arrogance insults the ancient pacts!",
                f"The Oracle's patience wears thin as spider silk!"
            ],
            "cruel": [
                f"Suffer well, child. The {theme} feeds on doubt.",
                f"Each wrong answer tightens the noose...",
                f"Your fear is exquisite—do continue."
            ],
            "indifferent": [
                f"The void watches. The void waits.",
                f"{theme} knows no mercy, no favor.",
                f"Onward, seeker. The path cares not for your comfort."
            ]
        }
        
        templates = lore_templates.get(emotion, lore_templates["indifferent"])
        return random.choice(templates)
    
    def _select_fragment_style(self, emotion: str, intensity: float) -> str:
        """Select appropriate fragment style."""
        if emotion in ["wrathful", "cruel"] and intensity > 0.7:
            return "ancient_warning"
        elif emotion in ["amused", "mocking"]:
            return "mocking_observation"
        elif emotion in ["pleased"]:
            return "dark_wisdom"
        elif intensity > 0.8:
            return "eldritch_whisper"
        else:
            return "cryptic_prophecy"
    
    def _build_atmosphere(self, emotion: str, intensity: float, theme: str) -> dict:
        """Build atmospheric elements."""
        # Select mood based on emotion
        mood_map = {
            "pleased": "mysterious",
            "amused": "eerie",
            "mocking": "malevolent",
            "disappointed": "ominous",
            "wrathful": "suffocating",
            "cruel": "dread",
            "indifferent": "eerie"
        }
        
        mood = mood_map.get(emotion, "ominous")
        
        # Select visual hints (2-3 elements)
        num_visuals = 2 if intensity < 0.6 else 3
        visual_hints = random.sample(self.visual_hints_pool, num_visuals)
        
        # Select ambient sound
        ambient_sound = random.choice(self.ambient_sounds)
        
        return {
            "mood": mood,
            "visual_hints": visual_hints,
            "ambient_sound": ambient_sound,
            "intensity_level": "high" if intensity > 0.7 else "medium" if intensity > 0.4 else "low"
        }
    
    def _define_oracle_voice(self, emotion: str, intensity: float) -> dict:
        """Define the Oracle's voice characteristics."""
        intimacy_levels = {
            "pleased": "approving",
            "amused": "playful",
            "mocking": "distant",
            "disappointed": "cold",
            "wrathful": "overwhelming",
            "cruel": "intimate",
            "indifferent": "detached"
        }
        
        return {
            "tone": emotion,
            "emotion": emotion,
            "intimacy_level": intimacy_levels.get(emotion, "neutral"),
            "volume": "thunderous" if intensity > 0.8 else "whisper" if intensity < 0.3 else "normal"
        }
    
    def _create_narrative_hooks(
        self, 
        player_profile: dict, 
        last_theme: str,
        performance: str
    ) -> dict:
        """Create narrative hooks and observations."""
        name = player_profile.get("name", "Seeker")
        bravery = player_profile.get("bravery", 50)
        
        # Generate personal observation
        observations = [
            f"{name} trembles, yet persists...",
            f"The seeker's resolve wavers like candlelight.",
            f"{name}'s fear-scent grows sweeter.",
            f"Another step deeper into shadow, {name}.",
            f"The Oracle marks your progress, {name}."
        ]
        
        personal_observation = random.choice(observations)
        
        # Determine if we reference the last theme
        references_last_theme = random.random() > 0.3  # 70% chance
        
        return {
            "references_last_theme": references_last_theme,
            "foreshadows_next": random.random() > 0.6,  # 40% chance
            "personal_observation": personal_observation,
            "hints_at_rewards": bravery > 70 and performance in ["excellent", "good"]
        }
    
    def _estimate_duration(self, text: str) -> int:
        """Estimate reading duration in seconds."""
        # Rough estimate: 3 words per second reading
        word_count = len(text.split())
        return max(3, min(8, int(word_count / 3) + 1))
    
    def generate_lore(self, context: dict) -> dict:
        """
        Generate horror lore based on the current context.
        
        Args:
            context: Dictionary containing:
                - theme: Horror theme or subgenre
                - difficulty: Current difficulty level
                - user_profile: User's preferences and history
                
        Returns:
            Dictionary containing lore fragment with full structure
        """
        return self.whisper_between_chambers(
            player_profile=context.get("user_profile", {}),
            last_theme=context.get("theme", "horror"),
            emotion=context.get("emotion", "indifferent"),
            performance=context.get("performance", "average")
        )
    
    def generate_backstory(self, movie_data: dict) -> str:
        """
        Generate a horror-themed backstory for a movie.
        
        Args:
            movie_data: Dictionary containing movie information
            
        Returns:
            Generated backstory text
        """
        title = movie_data.get("title", "Unknown Film")
        year = movie_data.get("year", "unknown era")
        
        backstories = [
            f"In {year}, {title} emerged from the void—a curse captured on celluloid.",
            f"They say {title} shouldn't have been made. The shadows disagreed.",
            f"{title}... a film that watches back. Released {year}, forgotten never.",
            f"The Oracle remembers when {title} first whispered into the darkness ({year})."
        ]
        
        return random.choice(backstories)
    
    def generate_transition(
        self, 
        from_room: str, 
        to_room: str, 
        performance: str,
        player_profile: dict = None
    ) -> str:
        """
        Generate atmospheric transition text between quiz rooms.
        
        Args:
            from_room: Current room name
            to_room: Next room name
            performance: User's performance (e.g., "excellent", "poor")
            player_profile: Optional player profile data
            
        Returns:
            Transition narrative text
        """
        if performance == "excellent":
            templates = [
                f"You conquered {from_room}. Now {to_room} beckons...",
                f"The path from {from_room} opens. {to_room} awaits your mastery.",
                f"Impressive. The Oracle grants passage to {to_room}."
            ]
        elif performance == "poor":
            templates = [
                f"You stumble from {from_room}, bloodied but unbowed. {to_room} will show no mercy.",
                f"Barely escaping {from_room}, you face {to_room}—perhaps your final chamber.",
                f"The Oracle frowns. {to_room} shall test whether you deserve to continue."
            ]
        else:  # average
            templates = [
                f"From {from_room} to {to_room}, the Oracle guides your uncertain steps.",
                f"{from_room} yields to {to_room}. The darkness deepens.",
                f"You proceed from {from_room} into {to_room}, neither celebrated nor condemned."
            ]
        
        return random.choice(templates)


def create_lore_node():
    """Factory function to create a lore whisperer node."""
    return LoreWhispererNode()

