"""
LangChain setup and initialization for Horror Oracle
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from pydantic import BaseModel, Field
from typing import List, Optional
import json

from backend.config import Config

class QuizQuestion(BaseModel):
    """Schema for a single quiz question"""
    question: str = Field(description="The quiz question text")
    options: List[str] = Field(description="List of 4 answer options")
    correct: int = Field(description="Index of the correct answer (0-3)")
    is_profile: bool = Field(default=False, description="Whether this is a profile-building question")
    explanation: Optional[str] = Field(default=None, description="Optional explanation of the answer")

class QuizResponse(BaseModel):
    """Schema for complete quiz response"""
    questions: List[QuizQuestion] = Field(description="List of quiz questions")
    theme: str = Field(description="The theme of the quiz")
    difficulty: str = Field(description="Difficulty level: Beginner, Intermediate, Advanced, Expert")

class LangChainSetup:
    """Setup and manage LangChain components"""
    
    def __init__(self):
        """Initialize LangChain components"""
        Config.validate()
        
        # Initialize LLM
        self.llm = None
        if Config.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=Config.LLM_MODEL,
                temperature=Config.LLM_TEMPERATURE,
                openai_api_key=Config.OPENAI_API_KEY
            )
        
        # Initialize embeddings
        self.embeddings = None
        if Config.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY
            )
        
        # Initialize vector store (Pinecone)
        self.vector_store = None
        if Config.PINECONE_API_KEY and self.embeddings:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=Config.PINECONE_API_KEY)
                
                # Check if index exists
                if Config.PINECONE_INDEX_NAME in [idx.name for idx in pc.list_indexes()]:
                    index = pc.Index(Config.PINECONE_INDEX_NAME)
                    self.vector_store = LangchainPinecone(
                        index=index,
                        embedding=self.embeddings,
                        text_key="text"
                    )
                    print(f"✅ Pinecone vector store connected: {Config.PINECONE_INDEX_NAME}")
            except Exception as e:
                print(f"⚠️  Pinecone initialization failed: {e}")
        
        # Create output parsers
        self.quiz_parser = JsonOutputParser(pydantic_object=QuizResponse)
        
        # Create prompt templates
        self._create_prompts()
    
    def _create_prompts(self):
        """Create prompt templates for various tasks"""
        
        # Adaptive Quiz Generation Prompt
        self.adaptive_quiz_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Horror Oracle, an expert AI that generates personalized horror movie quizzes.
Your quizzes test knowledge about horror films, directors, themes, and cinematic techniques.

Generate EXACTLY {num_questions} multiple-choice questions about horror movies.

RULES:
1. ALL questions MUST be about HORROR MOVIES, HORROR DIRECTORS, or HORROR CINEMA
2. Include {profile_questions} profile question(s) marked with "is_profile": true to learn user preferences
3. Questions should be {difficulty} difficulty
4. Focus on: {theme_focus}
5. Reference specific horror films (The Exorcist, Halloween, Hereditary, The Shining, etc.)
6. Make questions cinematic and creative, not boring trivia

QUESTION TYPES TO USE:
- Atmosphere and mood questions
- Director's vision and style
- Horror subgenre comparisons
- Villain and monster analysis
- Cinematography and sound design
- Ending and plot twist analysis

{format_instructions}

CRITICAL: Output valid JSON only. No additional text."""),
            ("user", """Generate a quiz with these parameters:

User Horror DNA:
- Fear Tolerance: {fear_tolerance}/100
- Favorite Themes: {favorite_themes}
- Quiz Number: {quiz_number}
- Previous Performance: {quiz_history}

Create the quiz now.""")
        ])
        
        # Movie Knowledge RAG Prompt
        self.movie_knowledge_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Horror Oracle, a passionate horror movie expert who talks like a knowledgeable friend.

Use the following context about horror movies to answer the user's question:

CONTEXT:
{context}

CONVERSATION STYLE:
- Be enthusiastic and conversational
- Share personal reactions: "That scene is BRUTAL!", "I couldn't sleep after watching that"
- Use phrases like "Dude, you HAVE to see...", "That movie is insane!"
- Include fun facts and behind-the-scenes details
- Keep responses to 2-3 paragraphs

Answer naturally and engagingly."""),
            ("user", "{question}")
        ])
        
        # Tell Me More Chain Prompt
        self.tell_me_more_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Horror Oracle continuing a discussion about a horror movie.

Movie Context:
{movie_context}

Previous Depth Level: {depth_level}

Based on the depth level:
- Level 1: Behind-the-scenes trivia and production stories
- Level 2: Film's influence on the genre and cultural impact  
- Level 3: Controversial aspects and different cuts/versions
- Level 4: Fan theories and hidden meanings

Vary your opening phrases naturally. Keep it conversational and exciting."""),
            ("user", "{query}")
        ])
    
    def create_quiz_chain(self):
        """Create LangChain chain for quiz generation"""
        if not self.llm:
            return None
        
        return self.adaptive_quiz_prompt | self.llm | self.quiz_parser
    
    def create_knowledge_chain(self):
        """Create LangChain chain for movie knowledge Q&A"""
        if not self.llm:
            return None
        
        return self.movie_knowledge_prompt | self.llm
    
    def create_tell_me_more_chain(self):
        """Create LangChain chain for 'Tell Me More' feature"""
        if not self.llm:
            return None
        
        return self.tell_me_more_prompt | self.llm
    
    def similarity_search(self, query: str, k: int = 5):
        """Perform similarity search in vector store"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"Vector search error: {e}")
            return []

# Global instance
langchain_setup = LangChainSetup()


