"""
LangChain-powered Movie Knowledge RAG System
Retrieval-Augmented Generation for horror movie information
"""
from typing import Dict, List, Optional
import random

from backend.langchain_setup import langchain_setup
from backend.config import Config

class MovieKnowledgeRAG:
    """RAG system for horror movie knowledge"""
    
    def __init__(self):
        """Initialize RAG system"""
        self.chain_setup = langchain_setup
        self.knowledge_chain = self.chain_setup.create_knowledge_chain()
        self.tell_me_more_chain = self.chain_setup.create_tell_me_more_chain()
        
        # Conversation depth tracker
        self.conversation_depth = {}
    
    def answer_query(
        self,
        query: str,
        query_type: str = "general",
        movie_context: Optional[Dict] = None
    ) -> str:
        """
        Answer a horror movie query using RAG
        
        Args:
            query: User's question
            query_type: Type of query (specific_movie, tell_me_more, general, etc.)
            movie_context: Optional movie details for context
        
        Returns:
            Response string
        """
        
        # Handle "Tell Me More" queries
        if query_type == "tell_me_more" and movie_context:
            return self._handle_tell_me_more(query, movie_context)
        
        # Perform similarity search for context
        context_docs = self.chain_setup.similarity_search(query, k=3)
        context_text = "\n\n".join(context_docs) if context_docs else "No specific context available."
        
        # Generate response using LangChain
        if self.knowledge_chain:
            try:
                response = self.knowledge_chain.invoke({
                    "context": context_text,
                    "question": query
                })
                return response.content
            except Exception as e:
                print(f"RAG error: {e}")
                return self._fallback_response(query, query_type)
        
        return self._fallback_response(query, query_type)
    
    def _handle_tell_me_more(self, query: str, movie_context: Dict) -> str:
        """Handle progressive 'Tell Me More' queries"""
        
        movie_title = movie_context.get('title', 'this movie')
        depth_key = f"depth_{movie_title.lower()}"
        
        # Increment depth level (1-4)
        current_depth = self.conversation_depth.get(depth_key, 0)
        current_depth = (current_depth % 4) + 1
        self.conversation_depth[depth_key] = current_depth
        
        # Format movie context
        context_str = f"""
        Title: {movie_context.get('title')}
        Year: {movie_context.get('year', 'N/A')}
        Director: {movie_context.get('director', 'Unknown')}
        Plot: {movie_context.get('plot', 'N/A')}
        """
        
        if self.tell_me_more_chain:
            try:
                response = self.tell_me_more_chain.invoke({
                    "movie_context": context_str,
                    "depth_level": current_depth,
                    "query": query
                })
                return response.content
            except Exception as e:
                print(f"Tell Me More error: {e}")
                return self._fallback_tell_me_more(movie_title, current_depth)
        
        return self._fallback_tell_me_more(movie_title, current_depth)
    
    def _fallback_tell_me_more(self, movie_title: str, depth: int) -> str:
        """Fallback responses for Tell Me More"""
        
        fallback_templates = {
            1: [
                f"Here's something wild about {movie_title} - the practical effects were all done without CGI! They used gallons of corn syrup and food coloring for the blood.",
                f"Fun fact: {movie_title} was actually banned in several countries! The censors thought it was too intense for audiences.",
                f"The production story is insane - they filmed {movie_title} in an actual abandoned location that locals claimed was haunted!"
            ],
            2: [
                f"What most people don't realize is that {movie_title} inspired a whole wave of copycats. It basically created its own subgenre.",
                f"After {movie_title} came out, horror directors completely changed their approach to the genre.",
                f"The cultural impact of {movie_title} was massive - it defined horror for an entire generation."
            ],
            3: [
                f"There's actually a darker version of {movie_title} - the unrated cut shows scenes that were way too intense for theaters.",
                f"The censors went crazy over {movie_title}. In some countries, they cut out entire scenes.",
                f"The director's cut of {movie_title} is completely different from what most people saw in theaters."
            ],
            4: [
                f"Fans have this theory that {movie_title} is actually connected to other horror films through hidden Easter eggs.",
                f"If you look closely, {movie_title} has tons of hidden meanings and symbolism that most viewers miss.",
                f"The director confirmed that {movie_title} has a secret alternate ending that completely changes everything."
            ]
        }
        
        responses = fallback_templates.get(depth, fallback_templates[1])
        return random.choice(responses)
    
    def _fallback_response(self, query: str, query_type: str) -> str:
        """Fallback responses when LangChain is unavailable"""
        
        fallback_templates = {
            "bloodiest": "You want the bloody stuff! Dead Alive (1992) is INSANE - they used 300 liters of fake blood per minute in the final scene! Evil Dead 2013 is also completely drenched in blood. And if you want something recent, Terrifier 2 made people literally pass out in theaters from the gore!",
            
            "zombies": "Zombie movies? I got you covered! Train to Busan is absolutely incredible - fast zombies and it'll make you cry. 28 Days Later changed the game with running zombies. And Dawn of the Dead (both versions) are must-watches. Shaun of the Dead if you want laughs with your zombies!",
            
            "vampires": "Vampire picks! Let the Right One In is hauntingly beautiful. 30 Days of Night has terrifying vampires in Alaska. The Lost Boys is an 80s classic. And What We Do in the Shadows if you want comedy. Each brings something totally different to vampire lore!",
            
            "slashers": "Slasher time! Halloween basically created the template - Michael Myers is pure evil. Scream revitalized the genre with meta-commentary. Friday the 13th has the iconic Jason. And A Nightmare on Elm Street with Freddy Krueger is a must-watch!",
            
            "general": "I love talking horror! What specifically are you in the mood for? Slashers, zombies, vampires, or something really messed up?"
        }
        
        return fallback_templates.get(query_type, fallback_templates["general"])

# Global instance
movie_rag = MovieKnowledgeRAG()


