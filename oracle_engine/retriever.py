"""
Horror Data Retriever Module
Provides retrieval functionality for horror movie data using Pinecone and SQLite.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone and OpenAI clients
try:
    from pinecone import Pinecone
    from openai import OpenAI
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("[WARN] Pinecone or OpenAI not available for retrieval")

import sqlite3


class HorrorDataRetriever:
    """
    Retrieves horror movie data from Pinecone vector store and SQLite database.
    Used by Quiz Builder to ground questions in real horror films and lore.
    """
    
    def __init__(self):
        """Initialize retriever with Pinecone and database connections."""
        self.pinecone_client = None
        self.index = None
        self.openai_client = None
        self.db_conn = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Set up Pinecone, OpenAI, and SQLite connections."""
        try:
            # Pinecone setup
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            if pinecone_api_key and PINECONE_AVAILABLE:
                self.pinecone_client = Pinecone(api_key=pinecone_api_key)
                self.index = self.pinecone_client.Index("horror-movies")
                print("[OK] Retriever: Pinecone index connected")
            else:
                print("[WARN] Retriever: Pinecone not available")
            
            # OpenAI setup (for embeddings)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                print("[OK] Retriever: OpenAI client initialized")
            else:
                print("[WARN] Retriever: OpenAI not available")
            
            # SQLite setup
            try:
                self.db_conn = sqlite3.connect('horror_movies.db', check_same_thread=False)
                print("[OK] Retriever: SQLite database connected")
            except Exception as e:
                print(f"[WARN] Retriever: SQLite connection failed: {e}")
                
        except Exception as e:
            print(f"[WARN] Retriever initialization warning: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        if not self.openai_client:
            return []
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {e}")
            return []
    
    def retrieve_horror_docs(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Retrieve horror movie documents relevant to the query.
        
        Args:
            query: Search query (e.g., "classic slasher films", "zombie horror")
            top_k: Number of documents to retrieve
            
        Returns:
            List of document dictionaries with movie information
        """
        # ALWAYS use fallback data which has better classic horror film trivia
        # Pinecone index seems to have documentary data, fallback has classic films
        print("[RETRIEVER] Using curated classic horror film data for trivia")
        return self._fallback_horror_data(query)
        
        # Original Pinecone retrieval code (disabled for now - uncomment to use Pinecone)
        # if not self.index or not self.openai_client:
        #     print("[WARN] Retrieval unavailable, using fallback data")
        #     return self._fallback_horror_data(query)
        
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return self._fallback_horror_data(query)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract and format documents
            documents = []
            for match in results.get('matches', []):
                metadata = match.get('metadata', {})
                documents.append({
                    'title': metadata.get('title', 'Unknown'),
                    'year': metadata.get('year', ''),
                    'director': metadata.get('director', ''),
                    'plot': metadata.get('overview', metadata.get('plot', '')),
                    'genre': metadata.get('genre', ''),
                    'score': match.get('score', 0.0)
                })
            
            print(f"[RETRIEVER] Retrieved {len(documents)} documents for query: {query}")
            return documents
            
        except Exception as e:
            print(f"[ERROR] Pinecone retrieval failed: {e}")
            return self._fallback_horror_data(query)
    
    def get_random_horror_movies(self, theme: str = "general_horror", limit: int = 10) -> List[Dict]:
        """
        Get random horror movies from database for quiz generation.
        
        Args:
            theme: Horror subgenre/theme
            limit: Number of movies to retrieve
            
        Returns:
            List of movie dictionaries
        """
        if not self.db_conn:
            return self._fallback_horror_data(theme)
        
        try:
            cursor = self.db_conn.cursor()
            
            # Query database for horror movies
            cursor.execute('''
                SELECT title, original_title, release_date, overview, popularity
                FROM movies
                WHERE overview IS NOT NULL
                ORDER BY RANDOM()
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            movies = []
            for row in rows:
                movies.append({
                    'title': row[0] or row[1],
                    'year': row[2][:4] if row[2] else '',
                    'plot': row[3],
                    'popularity': row[4]
                })
            
            print(f"[RETRIEVER] Retrieved {len(movies)} random movies from database")
            return movies
            
        except Exception as e:
            print(f"[ERROR] Database retrieval failed: {e}")
            return self._fallback_horror_data(theme)
    
    def _fallback_horror_data(self, query: str) -> List[Dict]:
        """
        Fallback horror movie data when retrieval is unavailable.
        Returns curated list of classic horror films for trivia.
        """
        print("[RETRIEVER] Using fallback horror data")
        
        fallback_movies = [
            {
                'title': 'The Exorcist',
                'year': '1973',
                'director': 'William Friedkin',
                'plot': 'A young girl becomes possessed by a demon named Pazuzu, and her mother seeks help from two priests.',
                'trivia': 'The demon possessing Regan is named Pazuzu, an ancient Assyrian demon.'
            },
            {
                'title': 'Halloween',
                'year': '1978',
                'director': 'John Carpenter',
                'plot': 'Michael Myers escapes from a mental institution and returns to his hometown to continue his killing spree.',
                'trivia': 'Michael Myers killed 5 people in the original 1978 film.'
            },
            {
                'title': 'The Thing',
                'year': '1982',
                'director': 'John Carpenter',
                'plot': 'A research team in Antarctica discovers a shape-shifting alien that can assume the form of its victims.',
                'trivia': 'The blood test scene is used to identify who is infected by the alien.'
            },
            {
                'title': 'A Nightmare on Elm Street',
                'year': '1984',
                'director': 'Wes Craven',
                'plot': 'Freddy Krueger, a burned killer, haunts teenagers in their dreams on Elm Street.',
                'trivia': 'Freddy Krueger wears a red and green striped sweater.'
            },
            {
                'title': 'The Shining',
                'year': '1980',
                'director': 'Stanley Kubrick',
                'plot': 'A family heads to an isolated hotel where an evil presence drives the father into violent madness.',
                'trivia': 'Room 237 is the forbidden room Danny is warned never to enter.'
            },
            {
                'title': 'Psycho',
                'year': '1960',
                'director': 'Alfred Hitchcock',
                'plot': 'A secretary embezzles money and encounters Norman Bates at the Bates Motel.',
                'trivia': 'Considered the first modern slasher film, establishing many genre conventions.'
            },
            {
                'title': 'Night of the Living Dead',
                'year': '1968',
                'director': 'George A. Romero',
                'plot': 'Zombies rise from the dead and terrorize survivors barricaded in a farmhouse.',
                'trivia': 'This film started the modern zombie genre and established the slow-moving zombie archetype.'
            },
            {
                'title': 'The Texas Chain Saw Massacre',
                'year': '1974',
                'director': 'Tobe Hooper',
                'plot': 'A group of friends encounters a family of cannibals, including the chainsaw-wielding Leatherface.',
                'trivia': 'Inspired by real-life serial killer Ed Gein who made masks from human skin.'
            },
            {
                'title': 'Hellraiser',
                'year': '1987',
                'director': 'Clive Barker',
                'plot': 'A puzzle box opens a gateway to the Cenobites, sadomasochistic beings from another dimension.',
                'trivia': 'The puzzle box is called the Lament Configuration.'
            },
            {
                'title': 'The Ring',
                'year': '2002',
                'director': 'Gore Verbinski',
                'plot': 'A cursed videotape kills anyone who watches it seven days later.',
                'trivia': 'Based on the Japanese film Ringu (1998) which started the J-horror wave in America.'
            },
            {
                'title': 'Get Out',
                'year': '2017',
                'director': 'Jordan Peele',
                'plot': 'A young Black man visits his white girlfriend\'s family estate and uncovers a disturbing secret.',
                'trivia': 'The hypnotic trigger is a teacup and spoon stirring, which sends Chris to the Sunken Place.'
            },
            {
                'title': 'The Conjuring',
                'year': '2013',
                'director': 'James Wan',
                'plot': 'Paranormal investigators Ed and Lorraine Warren help the Perron family being terrorized by a demon.',
                'trivia': 'The Warrens keep the possessed Annabelle doll in their occult museum.'
            },
            {
                'title': 'It',
                'year': '2017',
                'director': 'Andy Muschietti',
                'plot': 'A group of kids face off against the shape-shifting entity Pennywise the Clown.',
                'trivia': 'Pennywise returns to Derry every 27 years to feed on children.'
            },
            {
                'title': 'Saw',
                'year': '2004',
                'director': 'James Wan',
                'plot': 'Two men wake up in a bathroom and must follow the sadistic instructions of the Jigsaw Killer.',
                'trivia': 'The Jigsaw Killer\'s real name is John Kramer. He doesn\'t consider himself a murderer but someone who makes people appreciate life.'
            },
            {
                'title': 'Alien',
                'year': '1979',
                'director': 'Ridley Scott',
                'plot': 'The crew of the Nostromo encounters a deadly extraterrestrial creature.',
                'trivia': 'The ship\'s computer is called MOTHER.'
            },
        ]
        
        return fallback_movies


# Singleton instance for easy import
_retriever_instance = None

def get_retriever() -> HorrorDataRetriever:
    """Get singleton instance of HorrorDataRetriever."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = HorrorDataRetriever()
    return _retriever_instance

