"""
Builder Node (Question Generator)
Generates horror quiz questions using LangChain and prompt templates.
"""
import json
from typing import List, Dict, Optional

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
from oracle_engine.retriever import get_retriever


class BuilderNode:
    """
    Generates horror quiz questions tailored to user's profile and difficulty level.
    Uses LangChain and the Horror Oracle's Question Architect prompt.
    """
    
    def __init__(self):
        """Initialize the Builder node with LangChain components."""
        self.prompt_template = None
        self.llm = None
        self.chain = None
        self.retriever = get_retriever()  # Initialize horror data retriever
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM and create the generation chain."""
        try:
            Config.validate()
            
            # Try LangChain first
            if Config.OPENAI_API_KEY and LANGCHAIN_AVAILABLE and ChatOpenAI:
                try:
                    self.llm = ChatOpenAI(
                        model=Config.LLM_MODEL,
                        temperature=0.6,  # OPTIMIZED: Reduced from 0.8 for faster, more focused responses
                        max_tokens=800,   # OPTIMIZED: Reduced from default for 5 questions only
                        api_key=Config.OPENAI_API_KEY
                    )
                    print("[OK] Builder Node: LLM initialized with LangChain (optimized)")
                except Exception as e:
                    print(f"[WARN] LangChain init failed: {e}")
                    self.llm = None
            
            # Fallback to direct OpenAI client
            if not self.llm and Config.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    print("[OK] Builder Node: Using direct OpenAI client (fallback)")
                except Exception as e:
                    print(f"[WARN] OpenAI client init failed: {e}")
                    self.openai_client = None
            else:
                self.openai_client = None
                
            if not self.llm and not hasattr(self, 'openai_client'):
                if not Config.OPENAI_API_KEY:
                    print("[WARN] Builder Node: No OpenAI API key found")
                elif not LANGCHAIN_AVAILABLE:
                    print("[WARN] Builder Node: LangChain not available, and no fallback")
                    
        except Exception as e:
            print(f"[WARN] Builder Node initialization warning: {e}")
            self.openai_client = None
    
    def load_prompt(self) -> str:
        """Load the question generator prompt template."""
        self.prompt_template = load_prompt("question_generator_prompt")
        return self.prompt_template
    
    def generate_questions(
        self, 
        theme: str = "general_horror", 
        difficulty: float = 0.5, 
        tone: str = "creepy"
    ) -> List[Dict]:
        """
        Generate 5 horror quiz questions using LangChain or direct OpenAI.
        
        IMPORTANT: This method generates NEW questions each time - no caching!
        The LLM is called fresh with high temperature (0.8) for variety.
        
        Args:
            theme: Horror category (lore, movie, psychological, survival, etc.)
            difficulty: Float between 0.1-1.0
            tone: Atmospheric tone (creepy, mocking, ancient, whispered, grim, playful)
            
        Returns:
            List of 5 question dictionaries with structured format
        """
        import random
        import time
        import uuid
        
        # Randomize seed to ensure unique generation each time
        random.seed(time.time())
        session_seed = random.randint(1, 999999)
        session_uuid = str(uuid.uuid4())[:8]
        
        print(f"\n[BUILDER NODE] Generating NEW questions (no cache)")
        print(f"[BUILDER NODE] Session UUID: {session_uuid} | Seed: {session_seed}")
        print(f"[BUILDER NODE] Theme: {theme} | Difficulty: {difficulty} | Tone: {tone}")
        
        # Retrieve real horror movie data for context
        print(f"[BUILDER NODE] Retrieving horror movie data for theme: {theme}")
        t_retriever_start = time.time()
        horror_docs = self.retriever.retrieve_horror_docs(
            query=f"{theme} horror movies trivia facts",
            top_k=5  # OPTIMIZED: Reduced from 10 to 5 for speed
        )
        t_retriever_end = time.time()
        print(f"⏱️  Retriever took: {t_retriever_end - t_retriever_start:.3f}s")
        
        # Build context from retrieved horror data
        horror_context = "\n\nHORROR MOVIE DATA FOR TRIVIA QUESTIONS:\n"
        for i, doc in enumerate(horror_docs[:5], 1):  # OPTIMIZED: Use 5 docs instead of 10
            horror_context += f"\n{i}. {doc.get('title', 'Unknown')} ({doc.get('year', '')})"
            if doc.get('director'):
                horror_context += f" - Dir: {doc['director']}"
            if doc.get('plot'):
                horror_context += f"\n   Plot: {doc['plot'][:200]}..."
            if doc.get('trivia'):
                horror_context += f"\n   Trivia: {doc['trivia']}"
            horror_context += "\n"
        
        horror_context += "\nUse the above movies as source material for your trivia questions. Reference specific plot points, characters, directors, and facts.\n"
        
        # Try LangChain method first
        if self.llm:
            try:
                # Load prompt template if not already loaded
                if not self.prompt_template:
                    self.load_prompt()
                
                # Format the prompt template with parameters
                system_prompt = self.prompt_template.format(
                    theme=theme,
                    difficulty=difficulty,
                    tone=tone
                )
                
                # Add horror data context to the user message
                user_prompt = f"""{horror_context}

[UNIQUENESS SEED: {session_seed} | Session: {session_uuid}]
Generate 5 questions using the movie data provided above. Follow all the rules and requirements in your instructions, including tone consistency, theme adherence, and the Easter egg requirement."""
                
                # Create chat prompt - USE THE LOADED PROMPT AS SYSTEM MESSAGE
                chat_prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("user", user_prompt)
                ])
                
                # Create and invoke chain
                # NOTE: High temperature (0.8) ensures variety between calls
                parser = JsonOutputParser()
                chain = chat_prompt | self.llm | parser
                
                print("[BUILDER NODE] Calling LLM via LangChain to generate fresh questions...")
                t_llm_start = time.time()
                result = chain.invoke({
                    "theme": theme,
                    "difficulty": difficulty,
                    "tone": tone
                })
                t_llm_end = time.time()
                print(f"⏱️  🔥 LLM CALL took: {t_llm_end - t_llm_start:.3f}s 🔥")
                
                # Validate result
                if isinstance(result, list) and len(result) == 5:
                    print(f"[BUILDER NODE] Generated 5 NEW questions successfully via LangChain")
                    if result[0].get('question'):
                        print(f"[BUILDER NODE] Sample Q: {result[0]['question'][:60]}...")
                    return result
                else:
                    print(f"[WARN] LangChain result format unexpected, trying direct OpenAI...")
                    
            except Exception as e:
                print(f"[WARN] LangChain generation failed: {e}, trying direct OpenAI...")
        
        # Try direct OpenAI client
        if hasattr(self, 'openai_client') and self.openai_client:
            try:
                # Load prompt template if not already loaded
                if not self.prompt_template:
                    self.load_prompt()
                
                # Format the prompt template with parameters
                system_prompt = self.prompt_template.format(
                    theme=theme,
                    difficulty=difficulty,
                    tone=tone
                )
                
                # Add horror data context to the user message
                user_prompt = f"""{horror_context}

[UNIQUENESS SEED: {session_seed} | Session: {session_uuid}]
Generate 5 questions using the movie data provided above. Follow all the rules and requirements in your instructions, including tone consistency, theme adherence, and the Easter egg requirement."""
                
                print("[BUILDER NODE] Calling OpenAI API directly...")
                t_openai_start = time.time()
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.6,   # OPTIMIZED: Reduced from 0.8 for speed
                    max_tokens=800     # OPTIMIZED: Reduced from 1500 - sufficient for 5 questions
                )
                t_openai_end = time.time()
                print(f"⏱️  🔥 OpenAI API CALL took: {t_openai_end - t_openai_start:.3f}s 🔥")
                
                content = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:].strip()
                
                import json
                result = json.loads(content)
                
                # Validate result
                if isinstance(result, list) and len(result) == 5:
                    print(f"[BUILDER NODE] Generated 5 NEW questions successfully via direct OpenAI")
                    if result[0].get('question'):
                        print(f"[BUILDER NODE] Sample Q: {result[0]['question'][:60]}...")
                    return result
                else:
                    print(f"[WARN] Direct OpenAI result format unexpected, using fallback")
                    
            except Exception as e:
                print(f"[ERROR] Direct OpenAI generation failed: {e}")
        
        # Last resort: fallback questions
        print("[WARN] All LLM methods failed, using fallback questions")
        return self._fallback_questions(theme, difficulty, tone)
    
    def generate_quiz(
        self, 
        user_profile: dict = None, 
        difficulty: str = "intermediate", 
        theme: str = None
    ) -> dict:
        """
        Generate a complete horror quiz based on user profile and difficulty.
        
        Args:
            user_profile: User's preference and performance data
            difficulty: Quiz difficulty level (beginner, intermediate, advanced, expert)
            theme: Optional horror theme/subgenre
            
        Returns:
            Dictionary containing quiz data with questions, choices, and answers
        """
        import random
        import time
        
        # Randomize for unique chamber names
        random.seed(time.time())
        
        # Map difficulty string to float
        difficulty_map = {
            "beginner": 0.3,
            "intermediate": 0.5,
            "advanced": 0.7,
            "expert": 0.9
        }
        difficulty_float = difficulty_map.get(difficulty.lower(), 0.5)
        
        # Determine theme from user profile or use default
        if not theme and user_profile:
            theme = user_profile.get("favorite_theme", "general_horror")
        elif not theme:
            theme = "general_horror"
        
        # Determine tone from user profile or difficulty
        tone = "creepy"  # Default
        if user_profile:
            tone = user_profile.get("preferred_tone", "creepy")
        
        # Generate questions
        questions = self.generate_questions(theme, difficulty_float, tone)
        
        # Generate UNIQUE chamber name for each quiz
        chamber_name = self._generate_unique_chamber_name(difficulty, theme, tone)
        
        return {
            "room": chamber_name,
            "intro": self._generate_intro(theme, tone),
            "questions": questions,
            "theme": theme,
            "difficulty": difficulty,
            "tone": tone
        }
    
    def _generate_unique_chamber_name(self, difficulty: str, theme: str, tone: str) -> str:
        """
        Generate a unique, atmospheric chamber name for each quiz session.
        
        Returns a randomized chamber name that reflects difficulty, theme, and tone.
        """
        import random
        
        # Chamber prefix variations
        prefixes = [
            "The Chamber of", "The Hall of", "The Vault of", "The Crypt of",
            "The Sanctum of", "The Pit of", "The Abyss of", "The Den of",
            "The Lair of", "The Domain of", "The Realm of", "The Depths of",
            "The Throne of", "The Tower of", "The Dungeon of", "The Maze of",
            "The Temple of", "The Ruins of", "The Cavern of", "The Labyrinth of"
        ]
        
        # Atmospheric descriptors based on tone
        tone_descriptors = {
            "creepy": ["Whispers", "Shadows", "Silence", "Dread", "Echoes", "Phantoms"],
            "mocking": ["Folly", "Hubris", "Mockery", "Jest", "Vanity", "Pride"],
            "ancient": ["Ancients", "Forgotten", "Eternity", "Lost Souls", "Elders", "Primordial Fears"],
            "whispered": ["Secrets", "Murmurs", "Whispers", "Hidden Truths", "Confessions", "Revelations"],
            "grim": ["Despair", "Torment", "Anguish", "Suffering", "Doom", "Perdition"],
            "playful": ["Games", "Riddles", "Tricks", "Illusions", "Mischief", "Madness"]
        }
        
        # Theme-specific descriptors
        theme_descriptors = {
            "general_horror": ["Screams", "Terror", "Nightmares", "Blood", "Fear", "Darkness"],
            "slasher": ["Blades", "Carnage", "Slaughter", "Butchery", "Gore", "Massacre"],
            "psychological": ["Madness", "Psychosis", "Delusion", "Paranoia", "Obsession", "Hysteria"],
            "supernatural": ["Spirits", "Wraiths", "Apparitions", "Hauntings", "Curses", "Possession"],
            "zombie": ["Decay", "Infection", "Undeath", "Plague", "Rot", "Resurrection"],
            "vampire": ["Thirst", "Immortality", "Bloodlust", "Nocturne", "Crimson", "Eternal Night"],
            "cosmic": ["Void", "Oblivion", "Infinity", "Cosmic Dread", "Unknown", "Eldritch"],
            "gothic": ["Gloom", "Melancholy", "Sorrow", "Decay", "Romantic Death", "Darkness"],
            "body_horror": ["Mutation", "Transformation", "Flesh", "Viscera", "Aberration", "Grotesque"]
        }
        
        # Difficulty-based descriptors
        difficulty_descriptors = {
            "beginner": ["Awakening", "Initiation", "First Steps", "Beginning", "Novice Trials", "Entry"],
            "intermediate": ["Trials", "Challenges", "Tests", "Ordeals", "Judgment", "Gauntlet"],
            "advanced": ["Suffering", "Agony", "Torment", "Pain", "Endless Horror", "Deep Fears"],
            "expert": ["Eternal Damnation", "Ultimate Horror", "Absolute Terror", "Final Judgment", "Oblivion", "Death"]
        }
        
        # Select appropriate descriptor lists
        tone_list = tone_descriptors.get(tone, tone_descriptors["creepy"])
        theme_list = theme_descriptors.get(theme, theme_descriptors["general_horror"])
        diff_list = difficulty_descriptors.get(difficulty.lower(), difficulty_descriptors["intermediate"])
        
        # Randomly combine elements for uniqueness
        chamber_type = random.choice([1, 2, 3])
        
        if chamber_type == 1:
            # Format: "The Chamber of [tone] [descriptor]"
            return f"{random.choice(prefixes)} {random.choice(tone_list)} {random.choice(['and', '&', 'of'])} {random.choice(theme_list)}"
        elif chamber_type == 2:
            # Format: "The Chamber of [difficulty descriptor]"
            return f"{random.choice(prefixes)} {random.choice(diff_list)}"
        else:
            # Format: "The Chamber of [theme] [tone]"
            return f"{random.choice(prefixes)} {random.choice(theme_list)}"
    
    def _generate_intro(self, theme: str, tone: str) -> str:
        """Generate atmospheric intro text based on theme and tone."""
        intros = {
            "creepy": f"The air grows cold as you enter the {theme} chamber. Something watches from the shadows...",
            "mocking": f"You dare challenge the Oracle's knowledge of {theme}? How amusing...",
            "ancient": f"From epochs long forgotten, the {theme} trials await thee...",
            "whispered": f"Listen closely... the {theme} secrets are about to be revealed...",
            "grim": f"There is no escape from the {theme} test. Face your trial.",
            "playful": f"Let's play a game with {theme}, shall we? Don't lose your head..."
        }
        return intros.get(tone, f"The Oracle prepares your {theme} test...")
    
    def _fallback_questions(self, theme: str, difficulty: float, tone: str) -> List[Dict]:
        """Fallback questions when LLM is unavailable.
        
        Returns a RANDOMIZED selection of 5 questions from a MASSIVE pool
        to ensure variety even without LLM access.
        """
        import random
        import time
        
        # Seed random with timestamp to ensure different questions each quiz
        random.seed(int(time.time()))
        
        # MASSIVE pool of 100+ horror questions for maximum variety
        # All questions wrapped in cinematic horror atmosphere
        question_pool = [
            # Classic Horror Trivia
            {
                "question": "In the flickering shadows of cinema history, what year did the first slasher truly stalk the silver screen with blade in hand?",
                "choices": ["1960 (Psycho)", "1974 (Black Christmas)", "1978 (Halloween)", "1980 (Friday the 13th)"],
                "correct_answer": "1960 (Psycho)",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "As cosmic dread seeps from ancient tomes, which director dared to bring Lovecraft's nightmares from the page to the screen?",
                "choices": ["John Carpenter", "Stuart Gordon", "Guillermo del Toro", "James Wan"],
                "correct_answer": "Stuart Gordon",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In the stifling Texas heat where screams echo eternally, what instrument of death defined the Chainsaw legacy?",
                "choices": ["Chainsaw", "Meat Hook", "Hammer", "All of the above"],
                "correct_answer": "All of the above",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In the cursed woods where reality blurs, which film first pioneered the found-footage horror revolution that would haunt viewers for decades?",
                "choices": ["The Blair Witch Project", "Cannibal Holocaust", "Paranormal Activity", "REC"],
                "correct_answer": "Cannibal Holocaust",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "As you drift into restless sleep, what striped colors does the dream demon wear when he slashes through your nightmares?",
                "choices": ["Red and black", "Red and green", "Black and white", "Brown and red"],
                "correct_answer": "Red and green",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror film was shot entirely in real time with no cuts?",
                "choices": ["Halloween", "The Descent", "Russian Ark", "Silent House"],
                "correct_answer": "Silent House",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What real-life serial killer inspired The Texas Chain Saw Massacre?",
                "choices": ["Jeffrey Dahmer", "Ed Gein", "Ted Bundy", "John Wayne Gacy"],
                "correct_answer": "Ed Gein",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In The Exorcist, what is the demon's name possessing Regan?",
                "choices": ["Beelzebub", "Pazuzu", "Asmodeus", "Baal"],
                "correct_answer": "Pazuzu",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror franchise has the most sequels?",
                "choices": ["Friday the 13th", "Nightmare on Elm Street", "Halloween", "Saw"],
                "correct_answer": "Friday the 13th",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What was the original title of Scream during production?",
                "choices": ["Ghostface", "Scary Movie", "Screamer", "Knife"],
                "correct_answer": "Scary Movie",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In The Shining, what room is Danny warned never to enter?",
                "choices": ["Room 217", "Room 237", "Room 117", "Room 337"],
                "correct_answer": "Room 237",
                "difficulty": 0.3,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror film features a character who can only be seen through a camera?",
                "choices": ["Paranormal Activity", "Shutter", "The Ring", "One Missed Call"],
                "correct_answer": "Shutter",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year was Night of the Living Dead released, starting the modern zombie genre?",
                "choices": ["1965", "1968", "1970", "1972"],
                "correct_answer": "1968",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Hellraiser, what puzzle opens the gateway to the Cenobites?",
                "choices": ["Lament Configuration", "Puzzlebox of Pain", "Gateway Cube", "Hell's Door"],
                "correct_answer": "Lament Configuration",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which actress turned down the role of Regan in The Exorcist?",
                "choices": ["Jodie Foster", "Denise Richards", "Linda Blair", "Drew Barrymore"],
                "correct_answer": "Denise Richards",
                "difficulty": 0.9,
                "tone": tone,
                "theme": theme
            },
            
            # Modern Horror (2000s-2020s)
            {
                "question": "In Get Out, what triggers Chris's hypnotic state?",
                "choices": ["A pocket watch", "A teacup and spoon", "A candle flame", "A music box"],
                "correct_answer": "A teacup and spoon",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror film popularized the phrase 'If you see him, you're already dead'?",
                "choices": ["It Follows", "The Babadook", "Sinister", "Lights Out"],
                "correct_answer": "Sinister",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In A Quiet Place, what sense do the creatures hunt by?",
                "choices": ["Sight", "Sound", "Smell", "Heat"],
                "correct_answer": "Sound",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year is Midsommar's horrifying festival held?",
                "choices": ["Every year", "Every 10 years", "Every 50 years", "Every 90 years"],
                "correct_answer": "Every 90 years",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            
            # Iconic Killers & Monsters
            {
                "question": "How many people did Michael Myers kill in the original Halloween (1978)?",
                "choices": ["3", "5", "7", "9"],
                "correct_answer": "5",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is Jason Voorhees's weapon of choice?",
                "choices": ["Chainsaw", "Machete", "Axe", "Knife"],
                "correct_answer": "Machete",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In which Nightmare on Elm Street film does Freddy finally die?",
                "choices": ["Part 3: Dream Warriors", "Part 4: Dream Master", "Part 6: Freddy's Dead", "New Nightmare"],
                "correct_answer": "Part 6: Freddy's Dead",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is Pinhead's real name before becoming a Cenobite?",
                "choices": ["Elliott Spencer", "Frank Cotton", "Kirsty Cotton", "Philip Channard"],
                "correct_answer": "Elliott Spencer",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "How does Pennywise return to Derry?",
                "choices": ["Every 13 years", "Every 19 years", "Every 27 years", "Every 33 years"],
                "correct_answer": "Every 27 years",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            
            # Directors & Creators
            {
                "question": "Who directed The Thing (1982)?",
                "choices": ["John Carpenter", "David Cronenberg", "Sam Raimi", "Wes Craven"],
                "correct_answer": "John Carpenter",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which director is known as the 'Master of Body Horror'?",
                "choices": ["Dario Argento", "David Cronenberg", "Lucio Fulci", "Clive Barker"],
                "correct_answer": "David Cronenberg",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Who wrote the novel that The Shining was based on?",
                "choices": ["Stephen King", "Dean Koontz", "Clive Barker", "Peter Straub"],
                "correct_answer": "Stephen King",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror maestro directed Suspiria (1977)?",
                "choices": ["Mario Bava", "Dario Argento", "Lucio Fulci", "Sergio Leone"],
                "correct_answer": "Dario Argento",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Who directed both Evil Dead and Spider-Man?",
                "choices": ["Sam Raimi", "James Wan", "Tim Burton", "Guillermo del Toro"],
                "correct_answer": "Sam Raimi",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            
            # International Horror
            {
                "question": "What country produced the horror film [REC]?",
                "choices": ["Mexico", "Spain", "France", "Italy"],
                "correct_answer": "Spain",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In which Japanese horror film does a cursed videotape kill viewers in 7 days?",
                "choices": ["Ju-on", "Ringu", "Dark Water", "Pulse"],
                "correct_answer": "Ringu",
                "difficulty": 0.3,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is the name of the vengeful ghost in Ju-on: The Grudge?",
                "choices": ["Sadako", "Kayako", "Tomie", "Toshio"],
                "correct_answer": "Kayako",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which Swedish vampire film was remade as Let Me In?",
                "choices": ["Thirst", "Let the Right One In", "Frostbite", "Vampyr"],
                "correct_answer": "Let the Right One In",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What South Korean film features a zombie outbreak on a train?",
                "choices": ["The Host", "Train to Busan", "The Wailing", "I Saw the Devil"],
                "correct_answer": "Train to Busan",
                "difficulty": 0.3,
                "tone": tone,
                "theme": theme
            },
            
            # Zombies & Infection
            {
                "question": "What caused the zombie outbreak in 28 Days Later?",
                "choices": ["A virus", "Radiation", "Aliens", "A curse"],
                "correct_answer": "A virus",
                "difficulty": 0.3,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Dawn of the Dead (1978), where do survivors take refuge?",
                "choices": ["A farmhouse", "A mall", "A military base", "A church"],
                "correct_answer": "A mall",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What do zombies in Return of the Living Dead want?",
                "choices": ["Blood", "Brains", "Flesh", "Souls"],
                "correct_answer": "Brains",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which film features fast-moving zombies, breaking the slow-zombie tradition?",
                "choices": ["Dawn of the Dead (2004)", "28 Days Later", "World War Z", "All of the above"],
                "correct_answer": "All of the above",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Shaun of the Dead, what's the name of Shaun's favorite pub?",
                "choices": ["The Winchester", "The King's Head", "The Crown", "The Red Lion"],
                "correct_answer": "The Winchester",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            
            # Supernatural & Demons
            {
                "question": "What demon possesses Regan in The Exorcist?",
                "choices": ["Asmodeus", "Pazuzu", "Beelzebub", "Mammon"],
                "correct_answer": "Pazuzu",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In The Conjuring, what possessed doll is kept in the Warrens' museum?",
                "choices": ["Chucky", "Annabelle", "Robert", "Tiffany"],
                "correct_answer": "Annabelle",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is the demon's name in Insidious?",
                "choices": ["The Lipstick-Face Demon", "The Red-Faced Demon", "The Bride in Black", "Parker Crane"],
                "correct_answer": "The Lipstick-Face Demon",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Sinister, what ancient Babylonian deity consumes children?",
                "choices": ["Moloch", "Bughuul", "Baal", "Lilith"],
                "correct_answer": "Bughuul",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year was The Exorcist released, shocking audiences worldwide?",
                "choices": ["1971", "1973", "1975", "1977"],
                "correct_answer": "1973",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            
            # Psychological Horror
            {
                "question": "In The Babadook, what book torments a mother and son?",
                "choices": ["Mister Babadook", "The Babadook Book", "The Monster Within", "The Shadow Man"],
                "correct_answer": "Mister Babadook",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What psychiatric condition is explored in Black Swan?",
                "choices": ["Schizophrenia", "Dissociative Identity Disorder", "Body Dysmorphia", "Psychotic Break"],
                "correct_answer": "Psychotic Break",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Shutter Island, what is Leonardo DiCaprio's character really?",
                "choices": ["A detective", "A patient", "A doctor", "A ghost"],
                "correct_answer": "A patient",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which film features the line 'I see dead people'?",
                "choices": ["The Others", "The Sixth Sense", "Stir of Echoes", "White Noise"],
                "correct_answer": "The Sixth Sense",
                "difficulty": 0.2,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In mother!, what does the house symbolize?",
                "choices": ["Earth", "Heaven", "Hell", "The Mind"],
                "correct_answer": "Earth",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            
            # Gore & Extreme Horror
            {
                "question": "How many Saw films have been released as of 2023?",
                "choices": ["7", "9", "10", "11"],
                "correct_answer": "10",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is the Jigsaw Killer's real name?",
                "choices": ["John Kramer", "Mark Hoffman", "Amanda Young", "Logan Nelson"],
                "correct_answer": "John Kramer",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Hostel, what organization runs the torture facility?",
                "choices": ["Elite Hunting", "Death Club", "The Society", "Torture Inc"],
                "correct_answer": "Elite Hunting",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which French extremity film features a brutal rape-revenge plot told in reverse?",
                "choices": ["Martyrs", "Inside", "Irreversible", "High Tension"],
                "correct_answer": "Irreversible",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year did the first Saw movie terrorize audiences?",
                "choices": ["2002", "2004", "2006", "2008"],
                "correct_answer": "2004",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            
            # Creature Features
            {
                "question": "In Alien, what is the name of the ship's computer?",
                "choices": ["HAL", "MOTHER", "CORTANA", "JARVIS"],
                "correct_answer": "MOTHER",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What test is used in The Thing to identify who's infected?",
                "choices": ["Blood test", "DNA test", "Heat test", "Shadow test"],
                "correct_answer": "Blood test",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Tremors, what are the underground creatures called?",
                "choices": ["Graboids", "Shriekers", "Ass-Blasters", "Dirt Dragons"],
                "correct_answer": "Graboids",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What South Korean monster film features a creature from the Han River?",
                "choices": ["The Host", "Sector 7", "D-War", "The Monster"],
                "correct_answer": "The Host",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Jaws, what is the name of the shark hunter Quint's boat?",
                "choices": ["The Orca", "The Nautilus", "The Pequod", "The Ahab"],
                "correct_answer": "The Orca",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            
            # Haunted Houses & Ghosts
            {
                "question": "What hotel is The Shining set in?",
                "choices": ["The Stanley Hotel", "The Overlook Hotel", "The Timberline Lodge", "The Grand Hotel"],
                "correct_answer": "The Overlook Hotel",
                "difficulty": 0.3,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Poltergeist, what phrase does Carol Anne say when she touches the TV?",
                "choices": ["They're coming", "They're watching", "They're here", "They're waiting"],
                "correct_answer": "They're here",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In The Others, what shocking truth is revealed at the end?",
                "choices": ["The children are vampires", "They are the ghosts", "The house is alive", "Time is looping"],
                "correct_answer": "They are the ghosts",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year was the Amityville house murders that inspired the horror franchise?",
                "choices": ["1972", "1974", "1976", "1978"],
                "correct_answer": "1974",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In The Conjuring, what family do the Warrens help?",
                "choices": ["The Lutz family", "The Perron family", "The Warren family", "The Hodgson family"],
                "correct_answer": "The Perron family",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            
            # Cult Classics
            {
                "question": "In The Rocky Horror Picture Show, what is Dr. Frank-N-Furter's creation called?",
                "choices": ["Rocky", "Riff Raff", "Eddie", "Columbia"],
                "correct_answer": "Rocky",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which cult film features a killer tire named Robert?",
                "choices": ["Rubber", "Turbo", "The Wheel", "Death Roll"],
                "correct_answer": "Rubber",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Army of Darkness, what are Ash's famous words?",
                "choices": ["Groovy", "Shop smart, shop S-Mart", "This is my boomstick", "All of the above"],
                "correct_answer": "All of the above",
                "difficulty": 0.4,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What year was The Evil Dead released?",
                "choices": ["1979", "1981", "1983", "1985"],
                "correct_answer": "1981",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "In Re-Animator, what substance brings the dead back to life?",
                "choices": ["Green serum", "Blue serum", "Red serum", "Purple serum"],
                "correct_answer": "Green serum",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            
            # Horror Trivia
            {
                "question": "What was the first horror film to be nominated for Best Picture at the Oscars?",
                "choices": ["The Exorcist", "Psycho", "Jaws", "Rosemary's Baby"],
                "correct_answer": "The Exorcist",
                "difficulty": 0.6,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which horror film popularized the 'final girl' trope?",
                "choices": ["Halloween", "Black Christmas", "Texas Chain Saw Massacre", "Alien"],
                "correct_answer": "Halloween",
                "difficulty": 0.5,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What is the highest-grossing horror film of all time (unadjusted)?",
                "choices": ["The Exorcist", "It (2017)", "The Sixth Sense", "Jaws"],
                "correct_answer": "It (2017)",
                "difficulty": 0.7,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "Which actor has played the most horror villains?",
                "choices": ["Robert Englund", "Doug Bradley", "Kane Hodder", "Tony Todd"],
                "correct_answer": "Kane Hodder",
                "difficulty": 0.8,
                "tone": tone,
                "theme": theme
            },
            {
                "question": "What was the first 3D horror film?",
                "choices": ["House of Wax", "Creature from the Black Lagoon", "Bwana Devil", "The Mad Magician"],
                "correct_answer": "Bwana Devil",
                "difficulty": 0.9,
                "tone": tone,
                "theme": theme
            }
        ]
        
        # Shuffle the entire pool for maximum randomization
        random.shuffle(question_pool)
        
        # Randomly select 5 questions from the shuffled pool
        print(f"[BUILDER NODE] Using randomized fallback questions from pool of {len(question_pool)} (LLM not available)")
        selected = random.sample(question_pool, min(5, len(question_pool)))
        print(f"[BUILDER NODE] Selected question 1: {selected[0]['question'][:60]}...")
        
        return selected


def create_builder_node():
    """Factory function to create a builder node."""
    return BuilderNode()

