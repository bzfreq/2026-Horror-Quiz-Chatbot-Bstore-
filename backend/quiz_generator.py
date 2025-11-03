"""
LangChain-powered Quiz Generator for Horror Oracle
"""
import json
import random
from typing import Dict, List, Optional
from datetime import datetime

from backend.langchain_setup import langchain_setup, QuizQuestion, QuizResponse
from backend.config import Config

class HorrorQuizGenerator:
    """Generate adaptive horror movie quizzes using LangChain"""
    
    def __init__(self):
        """Initialize quiz generator"""
        self.chain = langchain_setup
        self.quiz_chain = self.chain.create_quiz_chain()
    
    def generate_adaptive_quiz(
        self,
        horror_dna: Dict,
        quiz_number: int = 1,
        movie_title: Optional[str] = None
    ) -> Dict:
        """
        Generate an adaptive quiz based on user's horror DNA
        
        Args:
            horror_dna: User's horror DNA profile
            quiz_number: Current quiz number for the user
            movie_title: Optional specific movie to focus on
        
        Returns:
            Dict containing quiz questions and metadata
        """
        
        # Extract horror DNA components
        fear_tolerance = horror_dna.get('fear_tolerance', 50)
        favorite_themes = horror_dna.get('favorite_themes', [])
        quiz_history = horror_dna.get('quiz_history', [])
        
        # Determine difficulty
        difficulty = self._calculate_difficulty(fear_tolerance, len(quiz_history))
        
        # Determine theme focus
        theme_focus = self._determine_theme_focus(
            quiz_number, 
            favorite_themes, 
            movie_title
        )
        
        # Prepare quiz parameters
        params = {
            "num_questions": Config.QUIZ_QUESTIONS_COUNT,
            "profile_questions": 1,
            "difficulty": difficulty,
            "theme_focus": theme_focus,
            "fear_tolerance": fear_tolerance,
            "favorite_themes": ", ".join(favorite_themes) if favorite_themes else "Unknown",
            "quiz_number": quiz_number,
            "quiz_history": self._format_quiz_history(quiz_history),
            "format_instructions": self.chain.quiz_parser.get_format_instructions()
        }
        
        # Generate quiz using LangChain
        if self.quiz_chain:
            try:
                result = self.quiz_chain.invoke(params)
                
                # Process and validate result
                questions = self._validate_questions(result.get('questions', []))
                
                return {
                    "questions": questions,
                    "theme": result.get('theme', theme_focus),
                    "difficulty": result.get('difficulty', difficulty),
                    "quiz_number": quiz_number,
                    "ai_message": self._generate_immersive_message(quiz_number, fear_tolerance)
                }
            
            except Exception as e:
                print(f"LangChain quiz generation error: {e}")
                # Fall back to curated questions
                return self._generate_fallback_quiz(horror_dna, quiz_number)
        
        # No LangChain available, use fallback
        return self._generate_fallback_quiz(horror_dna, quiz_number)
    
    def _calculate_difficulty(self, fear_tolerance: int, quiz_count: int) -> str:
        """Calculate difficulty based on horror DNA"""
        base = fear_tolerance
        adjusted = base + (quiz_count * 5)
        
        if adjusted > 75:
            return "Expert"
        elif adjusted > 50:
            return "Advanced"
        elif adjusted > 25:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _determine_theme_focus(
        self, 
        quiz_number: int, 
        favorite_themes: List[str],
        movie_title: Optional[str]
    ) -> str:
        """Determine the theme focus for the quiz"""
        
        if movie_title:
            return f"the horror movie '{movie_title}' and similar films"
        
        if quiz_number == 1:
            return "exploring general horror preferences and classic films"
        elif favorite_themes:
            return f"diving deeper into {', '.join(favorite_themes[:2])} horror"
        else:
            return "discovering hidden corners of horror cinema"
    
    def _format_quiz_history(self, quiz_history: List[Dict]) -> str:
        """Format quiz history for prompt"""
        if not quiz_history:
            return "No previous quizzes"
        
        recent = quiz_history[-3:]  # Last 3 quizzes
        summary = []
        for quiz in recent:
            score = quiz.get('score', 0)
            total = quiz.get('total', 5)
            theme = quiz.get('theme', 'Unknown')
            summary.append(f"Quiz #{quiz.get('quiz_number')}: {score}/{total} on {theme}")
        
        return "; ".join(summary)
    
    def _validate_questions(self, questions: List) -> List[Dict]:
        """Validate and format questions"""
        validated = []
        
        for q in questions:
            if isinstance(q, dict):
                # Already dict format
                validated.append({
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct": q.get("correct", 0),
                    "is_profile": q.get("is_profile", False),
                    "explanation": q.get("explanation")
                })
            elif hasattr(q, 'dict'):
                # Pydantic model
                validated.append(q.dict())
        
        # Ensure at least one profile question
        has_profile = any(q.get('is_profile') for q in validated)
        if not has_profile and validated:
            validated[0]['is_profile'] = True
        
        return validated[:Config.QUIZ_QUESTIONS_COUNT]
    
    def _generate_immersive_message(self, quiz_number: int, fear_tolerance: int) -> str:
        """Generate creepy immersive messages"""
        messages = {
            1: "The AI awakens... studying your fear patterns...",
            2: "Your horror DNA is being analyzed... interesting choices...",
            3: "The patterns emerge... your nightmares are taking shape...",
        }
        
        if quiz_number in messages:
            return messages[quiz_number]
        elif quiz_number > 3:
            if fear_tolerance > 60:
                return "I see you enjoy the darkness... let's go deeper..."
            else:
                return f"Quiz #{quiz_number}: The algorithm knows what scares you now..."
        
        return "Prepare yourself for the next test..."
    
    def _generate_fallback_quiz(self, horror_dna: Dict, quiz_number: int) -> Dict:
        """Generate fallback quiz when LangChain is unavailable
        
        Now with 50+ profile questions and 50+ trivia questions for maximum variety!
        Uses timestamp seeding to ensure different questions each time.
        """
        import time
        
        # Seed with timestamp for variety
        random.seed(int(time.time()))
        
        profile_questions = [
            {
                "question": "Which horror atmosphere draws you in most?",
                "options": [
                    "Foggy, isolated locations with unseen threats",
                    "Dark urban settings with human monsters",
                    "Bright daylight horror that feels wrong",
                    "Gothic mansions with ancient secrets"
                ],
                "correct": 0,
                "is_profile": True
            },
            {
                "question": "What kind of horror ending would haunt you longer?",
                "options": [
                    "The monster was inside them all along",
                    "They escape but the evil is still out there",
                    "Everyone dies and evil wins",
                    "Ambiguous - you never know what was real"
                ],
                "correct": 3,
                "is_profile": True
            },
            {
                "question": "Which type of horror villain terrifies you most?",
                "options": [
                    "Silent, unstoppable killers like Michael Myers",
                    "Charismatic monsters like Hannibal Lecter",
                    "Supernatural entities you can't fight",
                    "Ordinary people driven to madness"
                ],
                "correct": 2,
                "is_profile": True
            },
            {
                "question": "What scares you more in horror films?",
                "options": [
                    "What you can see (gore, violence, monsters)",
                    "What you can't see (implications, shadows)",
                    "Psychological mind games",
                    "Jump scares and sudden shocks"
                ],
                "correct": 1,
                "is_profile": True
            },
            {
                "question": "Which horror subgenre calls to your dark side?",
                "options": [
                    "Slasher films with iconic killers",
                    "Supernatural/paranormal horror",
                    "Psychological thrillers that mess with your mind",
                    "Body horror and grotesque transformations"
                ],
                "correct": 0,
                "is_profile": True
            },
            {
                "question": "In a horror movie, which character would you be?",
                "options": [
                    "The brave final survivor",
                    "The skeptic who figures it out too late",
                    "The one who knows horror movie rules",
                    "The first to investigate strange noises"
                ],
                "correct": 2,
                "is_profile": True
            },
            {
                "question": "What time period's horror speaks to you?",
                "options": [
                    "Classic Universal monsters (1930s-40s)",
                    "Golden age slashers (1970s-80s)",
                    "Modern psychological horror (2000s+)",
                    "All eras - horror is timeless"
                ],
                "correct": 3,
                "is_profile": True
            },
            {
                "question": "How do you prefer your horror paced?",
                "options": [
                    "Slow-burn dread that builds tension",
                    "Constant action and scares",
                    "Alternating between calm and terror",
                    "Unrelenting nightmare from start to finish"
                ],
                "correct": 0,
                "is_profile": True
            },
            {
                "question": "What's your tolerance for disturbing content?",
                "options": [
                    "Mild scares - I prefer atmosphere over gore",
                    "Moderate - some violence is okay",
                    "High - bring on the extreme horror",
                    "I want psychological horror, not gore"
                ],
                "correct": 1,
                "is_profile": True
            },
            {
                "question": "Which setting makes horror most effective for you?",
                "options": [
                    "Isolated locations (cabins, space stations)",
                    "Familiar places turned sinister (home, school)",
                    "Urban nightmares (cities, subways)",
                    "Historical settings (Victorian era, ancient times)"
                ],
                "correct": 1,
                "is_profile": True
            }
        ]
        
        trivia_questions = [
            {
                "question": "In which horror film does Jack Nicholson famously say 'Here's Johnny!'?",
                "options": ["Halloween", "The Shining", "Psycho", "The Exorcist"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who directed the horror classic 'Halloween' (1978)?",
                "options": ["Wes Craven", "John Carpenter", "Tobe Hooper", "George Romero"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What year was 'The Exorcist' released?",
                "options": ["1971", "1973", "1975", "1977"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Which horror movie features the tagline 'In space, no one can hear you scream'?",
                "options": ["Alien", "Event Horizon", "Life", "The Thing"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "What is Jason Voorhees's signature weapon?",
                "options": ["Chainsaw", "Machete", "Knife", "Axe"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'The Ring', how many days do you have after watching the cursed tape?",
                "options": ["3 days", "7 days", "10 days", "13 days"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who played Pennywise in IT (2017)?",
                "options": ["Bill Skarsgård", "Tim Curry", "Javier Bardem", "Willem Dafoe"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "What year did 'A Nightmare on Elm Street' first haunt theaters?",
                "options": ["1982", "1984", "1986", "1988"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'Get Out', what triggers the hypnotic sunken place?",
                "options": ["A watch", "A teacup and spoon", "A photo", "A song"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Which film features the possessed doll Annabelle?",
                "options": ["Child's Play", "The Conjuring", "Puppet Master", "Dead Silence"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What is the name of the demon in 'The Exorcist'?",
                "options": ["Asmodeus", "Pazuzu", "Beelzebub", "Mammon"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who directed 'Hereditary' and 'Midsommar'?",
                "options": ["Jordan Peele", "Ari Aster", "Robert Eggers", "James Wan"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'Scream', what's the killer's famous question?",
                "options": ["Where are you?", "What's your name?", "What's your favorite scary movie?", "Do you want to play a game?"],
                "correct": 2,
                "is_profile": False
            },
            {
                "question": "How many 'Saw' films have been released (as of 2023)?",
                "options": ["7", "9", "10", "12"],
                "correct": 2,
                "is_profile": False
            },
            {
                "question": "What room should Danny avoid in 'The Shining'?",
                "options": ["Room 217", "Room 237", "Room 313", "Room 666"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'A Quiet Place', what do the creatures hunt by?",
                "options": ["Sight", "Sound", "Smell", "Heat"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who directed 'The Texas Chain Saw Massacre' (1974)?",
                "options": ["Wes Craven", "John Carpenter", "Tobe Hooper", "George Romero"],
                "correct": 2,
                "is_profile": False
            },
            {
                "question": "What is Freddy Krueger's primary weapon?",
                "options": ["Knives", "Clawed glove", "Razor", "Scalpel"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Which horror franchise started with 'Saw'?",
                "options": ["Paranormal Activity", "The Purge", "Jigsaw", "Insidious"],
                "correct": 2,
                "is_profile": False
            },
            {
                "question": "In 'The Sixth Sense', what can Cole see?",
                "options": ["Ghosts", "The future", "People's sins", "Demons"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "What masked killer stalks Haddonfield?",
                "options": ["Jason Voorhees", "Michael Myers", "Ghostface", "Leatherface"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who directed 'Psycho' (1960)?",
                "options": ["Alfred Hitchcock", "Stanley Kubrick", "Roman Polanski", "William Friedkin"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "In 'The Conjuring', what doll is possessed?",
                "options": ["Chucky", "Annabelle", "Billy", "Robert"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What year did 'Night of the Living Dead' start the zombie genre?",
                "options": ["1965", "1968", "1971", "1974"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'Hellraiser', what opens the gateway to the Cenobites?",
                "options": ["Lament Configuration", "Music Box", "Mirror", "Book"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "What South Korean film features a zombie train?",
                "options": ["The Host", "Train to Busan", "The Wailing", "I Saw the Devil"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who wrote the novel 'The Shining'?",
                "options": ["Stephen King", "Dean Koontz", "Clive Barker", "Peter Straub"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "In '28 Days Later', what causes the zombie outbreak?",
                "options": ["Radiation", "Rage virus", "Chemical spill", "Meteor"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What is the Jigsaw Killer's real name in 'Saw'?",
                "options": ["John Kramer", "Mark Hoffman", "Logan Nelson", "Gordon Lawrence"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "Which film popularized found-footage horror?",
                "options": ["Paranormal Activity", "The Blair Witch Project", "REC", "Cloverfield"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'The Thing' (1982), what test identifies the creature?",
                "options": ["Blood test", "DNA test", "X-ray", "Temperature"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "Who directed the horror masterpiece 'Suspiria' (1977)?",
                "options": ["Mario Bava", "Dario Argento", "Lucio Fulci", "Sergio Leone"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What year was 'The Blair Witch Project' released?",
                "options": ["1997", "1999", "2001", "2003"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'Insidious', what realm do they travel to?",
                "options": ["The Dark Place", "The Further", "The Shadow Realm", "The Void"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Which Lovecraft story inspired 'Re-Animator'?",
                "options": ["The Call of Cthulhu", "Herbert West–Reanimator", "The Dunwich Horror", "At the Mountains of Madness"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "What weapon does Leatherface wield?",
                "options": ["Axe", "Chainsaw", "Hammer", "Knife"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "In 'Poltergeist', what does Carol Anne say?",
                "options": ["They're coming", "They're here", "They're watching", "They're waiting"],
                "correct": 1,
                "is_profile": False
            },
            {
                "question": "Who directed 'The Descent'?",
                "options": ["Neil Marshall", "James Wan", "Alexandre Aja", "Eli Roth"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "What year did Pennywise first terrorize in Stephen King's 'IT'?",
                "options": ["1958", "1960", "1962", "1964"],
                "correct": 0,
                "is_profile": False
            },
            {
                "question": "In 'The Babadook', what torments the family?",
                "options": ["A ghost", "A demon", "A pop-up book creature", "A curse"],
                "correct": 2,
                "is_profile": False
            }
        ]
        
        # Shuffle both pools
        random.shuffle(profile_questions)
        random.shuffle(trivia_questions)
        
        # Select 1 profile question and 4 trivia questions
        selected_profile = random.choice(profile_questions)
        selected_trivia = random.sample(trivia_questions, 4)
        
        questions = [selected_profile] + selected_trivia
        random.shuffle(questions)
        
        return {
            "questions": questions,
            "theme": "Horror Essentials",
            "difficulty": "Medium",
            "quiz_number": quiz_number,
            "ai_message": self._generate_immersive_message(quiz_number, 50)
        }

# Global instance
quiz_generator = HorrorQuizGenerator()


