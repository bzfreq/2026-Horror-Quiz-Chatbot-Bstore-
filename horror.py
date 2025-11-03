from dotenv import load_dotenv
load_dotenv()

import os
import sys
import json
import requests
import uuid

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from urllib.parse import quote 
import sqlite3
import datetime
import random
from collections import defaultdict
import time
import threading

# Safe FAISS import check
try:
    import faiss
    print("✅ FAISS imported successfully")
except ModuleNotFoundError:
    print("⚠️ FAISS not installed. Run: pip install faiss-cpu")
    faiss = None

# Import Oracle Engine
from oracle_engine.main import start_first_quiz, evaluate_and_progress

# Import Redis Store
from oracle_engine.memory_store import RedisStore
store = RedisStore()

# Import Context Fusion Layer
from oracle_engine.context_fusion import state, build_fused_context

# Add this global dictionary for user sessions
session_histories = {}

# Import Conversational Memory
try:
    from oracle_engine.memory import TemporaryMemory
    session_memory = TemporaryMemory()
    print("✅ FAISS conversational memory initialized")
except Exception as e:
    print(f"⚠️ Failed to initialize FAISS memory: {e}")
    session_memory = None

# Import Conversation Layer
from oracle_conversation import (
    init_session,
    get_session,
    add_message_to_session,
    build_conversation_context,
    load_user_profile,
    sync_sessions,
    cleanup_old_sessions,
    oracle_conversation_node,
    should_use_conversation_layer,
    check_initiation_triggers,
    generate_proactive_message
)

# === FAISS Auto-Rebuilder (Local Horror Data) ===
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

def rebuild_faiss_index():
    print("🔄 Rebuilding FAISS index from local horror data ...")
    data_dir = Path("data/movie/horror_movies")
    if not data_dir.exists():
        print("❌ Directory not found:", data_dir)
        return
    embeddings = OpenAIEmbeddings()
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    docs = []
    for p in data_dir.rglob("*.txt"):
        try:
            text = p.read_text(encoding="utf-8")
            docs.extend(splitter.create_documents([text], metadatas=[{"source": p.name}]))
        except Exception as e:
            print("⚠️ Error reading", p, ":", e)
    if not docs:
        print("❌ No text files found.")
        return
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local("vector_data")
    print(f"✅ Re-indexed {len(docs)} local horror files into FAISS.")
# ================================================

# ----- CONFIG -----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === RAG Retrieval + Generation ===
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Set up vectorstore directory and clear old lock files
VECTOR_DIR = os.path.join(os.getcwd(), "chroma_data")
DB_FILE = os.path.join(VECTOR_DIR, "chroma.sqlite3")

# Clear Chroma DB file to fix Windows file lock issues
if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
        print("🧹 Old Chroma DB cleared to fix file lock issue.")
    except PermissionError:
        print(f"⚠️ Could not clear {DB_FILE} (locked by another process).")
    except Exception as e:
        print(f"⚠️ Error clearing {DB_FILE}: {e}")

# Initialize embeddings - upgrade openai package to 1.55.3+ to fix proxies issue
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Initialize Chroma cleanly after clearing old files
try:
    vectorstore = Chroma(persist_directory=VECTOR_DIR, embedding_function=embeddings)
    print("✅ Chroma vectorstore initialized")
except Exception as e:
    print(f"⚠️ ChromaDB initialization error: {e}")
    print("🔄 Attempting to fix by recreating the database...")
    try:
        import shutil
        # Backup old database if it exists
        backup_path = os.path.join(VECTOR_DIR, "chroma.sqlite3.backup")
        old_db = os.path.join(VECTOR_DIR, "chroma.sqlite3")
        if os.path.exists(old_db):
            shutil.copy2(old_db, backup_path)
            os.remove(old_db)
            print(f"✅ Backed up old database to {backup_path}")
        
        # Also try to remove the vectorstore directory if it exists
        if os.path.exists(VECTOR_DIR):
            try:
                shutil.rmtree(VECTOR_DIR)
                print("✅ Removed old vectorstore directory")
            except Exception as rm_error:
                print(f"⚠️ Could not remove vectorstore directory: {rm_error}")
        
        # Create fresh vectorstore
        vectorstore = Chroma(persist_directory=VECTOR_DIR, embedding_function=embeddings)
        print("✅ Created new ChromaDB database")
    except Exception as fix_error:
        print(f"❌ Failed to fix database: {fix_error}")
        print("⚠️ Creating vectorstore without persistence...")
        vectorstore = Chroma(embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini")

# Create retrieval chain using modern LCEL pattern
def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a horror movie expert. Use the following context to answer questions about horror movies:\n\n{context}"),
    ("human", "{question}")
])

# Create retrieval chain using LCEL
qa = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Create a chain for pre-retrieved context (used by RLOM)
qa_with_context = (
    {
        "context": RunnablePassthrough(),
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

def generate_oracle_response(user_question):
    """Retrieve horror context and generate a story-like answer."""
    try:
        response = qa.invoke(user_question)
        print(response)
        return response
    except Exception as e:
        print(f"⚠️ RAG error: {e}")
        # Fallback response if RAG fails
        return "The spirits are disturbed, but I'd love to talk horror with you! What kind of scares are you looking for?"

def generate_oracle_response_with_fusion(user_question, omdb_data=None, conversation_history=None, rlom_context=None):
    """Generate response using context fusion layer that combines RAG, OMDB, RLOM context, and conversation state."""
    try:
        # Retrieve RAG documents directly
        rag_docs = retriever.invoke(user_question)
        print(f"📚 Retrieved {len(rag_docs)} RAG documents")
        
        # Build fused context combining RAG, OMDB, and conversation state
        fused_context = build_fused_context(
            user_msg=user_question,
            rag_docs=rag_docs,
            omdb_data=omdb_data
        )
        
        # ===== RLOM: Prepend RLOM context if available (combines vectorstore + session memory) =====
        if rlom_context and rlom_context.strip():
            fused_context = f"{rlom_context}\n\n{fused_context}"
            print(f"✅ Enhanced with RLOM context (vectorstore + session memory)")
        
        # Update conversation state with user message (before getting LLM response)
        state.update_entities(user_question)
        
        # Build system message with context
        conversation_context_note = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context_note = "\n\nIMPORTANT: You are having an ongoing conversation. Previous messages are included below. Please remember what was discussed earlier (movies, characters, etc.) and refer back to them naturally in your response."
        
        system_message_content = f"""You are a horror movie expert. Use the following context to answer questions about horror movies:

{fused_context}{conversation_context_note}

When the user asks follow-up questions (like "who is he?", "how old?", "tell me more about that movie"), remember what you discussed in the previous messages and answer in context. Don't ask for clarification if the context is clear from the conversation."""
        
        # Build messages list starting with system prompt
        messages = [("system", system_message_content)]
        
        # Add conversation history if available
        if conversation_history and len(conversation_history) > 0:
            # Include last 8 messages (4 exchanges) for context
            recent_history = conversation_history[-8:]
            for msg in recent_history:
                # Handle both dict format {"role": "...", "content": "..."} and tuple format
                if isinstance(msg, dict):
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
                    role = msg[0]
                    content = msg[1]
                else:
                    continue
                
                if role == "user" or role == "human":
                    messages.append(("human", str(content)))
                elif role == "assistant" or role == "ai":
                    messages.append(("ai", str(content)))
            print(f"📝 Added {len(recent_history)} previous messages to context")
        
        # Add the current question
        messages.append(("human", user_question))
        
        # Create prompt template and convert to message format
        fused_prompt_template = ChatPromptTemplate.from_messages(messages)
        formatted_messages = fused_prompt_template.format_messages()
        
        # Call LLM with fused context and conversation history
        response = llm.invoke(formatted_messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        # Update conversation state with LLM answer (to capture entities from response)
        state.update_entities(user_question, answer)
        
        # Add turn to conversation history
        state.add_turn(user_question, answer)
        
        print(f"✅ Generated response with context fusion")
        return answer
    except Exception as e:
        print(f"⚠️ Context fusion error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to regular RAG if fusion fails
        return generate_oracle_response(user_question)

# === RLOM COGNITIVE LAYER =====================================================

# Purpose: sit ABOVE FAISS/Chroma and BELOW the Flask routes.

# R = Retrieval (ask vectorstore)

# L = Learning (LLM reasons over it)

# O = Observation (what is the user referring to right now?)

# M = Memory (store resolved turn for later)



from collections import deque



class ReferenceBuffer:

    """

    Holds the last N entities the user talked about so pronouns and vague phrases

    can be resolved BEFORE we call the LLM.

    """

    def __init__(self, maxlen=8):

        self.entities = deque(maxlen=maxlen)

        self.last_movie = None

        self.last_character = None

        self.last_killer = None

        self.last_time_ref = None



    def add_entity(self, kind: str, value: str):

        if not value:

            return

        entry = {"kind": kind, "value": value}

        self.entities.appendleft(entry)

        # fast-access slots

        if kind == "movie":

            self.last_movie = value

        elif kind == "character":

            self.last_character = value

        elif kind == "killer":

            self.last_killer = value

        elif kind == "time":

            self.last_time_ref = value



    def resolve(self, text: str) -> str:

        """

        Replace vague references ("he", "she", "the killer", "that movie")

        with the most recent concrete entity we know about.

        """

        lower = text.lower()
        
        # Create a working copy
        resolved_text = text



        # pronouns → killer / character / movie (priority order matters)
        # Use regex-style replacements but word boundary aware
        
        import re

        if self.last_killer:
            # Replace he/him/his with killer name
            resolved_text = re.sub(r'\bhe\b', self.last_killer, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bhim\b', self.last_killer, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bhis\b', self.last_killer + "'s", resolved_text, flags=re.IGNORECASE)
        elif self.last_character:
            resolved_text = re.sub(r'\bhe\b', self.last_character, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bhim\b', self.last_character, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bhis\b', self.last_character + "'s", resolved_text, flags=re.IGNORECASE)

        if self.last_character:
            resolved_text = re.sub(r'\bshe\b', self.last_character, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bher\b', self.last_character, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bhers\b', self.last_character + "'s", resolved_text, flags=re.IGNORECASE)



        # definite references

        if self.last_killer:
            resolved_text = re.sub(r'\bthe killer\b', self.last_killer, resolved_text, flags=re.IGNORECASE)

        if self.last_movie:
            resolved_text = re.sub(r'\bthat movie\b', self.last_movie, resolved_text, flags=re.IGNORECASE)
            resolved_text = re.sub(r'\bthe movie\b', self.last_movie, resolved_text, flags=re.IGNORECASE)



        # comparatives (needs previous target)

        if any(c in lower for c in ["better", "worse", "scarier", "more brutal"]):

            if self.last_movie:

                resolved_text = f"Compared to {self.last_movie}, {resolved_text}"



        # temporal

        if self.last_time_ref:

            resolved_text = re.sub(r'\bafter that\b', f"after {self.last_time_ref}", resolved_text, flags=re.IGNORECASE)



        return resolved_text





# global reference buffers per user
user_reference_buffers = {}

def get_or_create_reference_buffer(user_id):
    """Get or create a reference buffer for a specific user"""
    if user_id not in user_reference_buffers:
        user_reference_buffers[user_id] = ReferenceBuffer()
    return user_reference_buffers[user_id]

# Keep global buffer for backward compatibility
reference_buffer = ReferenceBuffer()



class SessionBridge:

    """

    Bridges your existing `session_memory` (TemporaryMemory) and the new RLOM logic

    so BOTH the LLM and the retriever see the same subject.

    """

    def __init__(self, session_mem, vec_retriever):

        self.session_mem = session_mem

        self.retriever = vec_retriever



    def remember_turn(self, user_id: str, user_text: str, bot_text: str, subject_hint: str = None):

        # push to TemporaryMemory if available

        if self.session_mem:

            try:

                self.session_mem.save_message(user_id, user_text, bot_text)

            except Exception as e:

                print(f"⚠️ session_memory save failed: {e}")



        # update reference buffer based on subject (user-specific)
        user_ref_buffer = get_or_create_reference_buffer(user_id)
        
        if subject_hint:

            # very simple classifier – Cursor can improve

            if "halloween" in subject_hint.lower():

                user_ref_buffer.add_entity("movie", "Halloween")

                user_ref_buffer.add_entity("killer", "Michael Myers")

            elif "saw" in subject_hint.lower():

                user_ref_buffer.add_entity("movie", "Saw")

                user_ref_buffer.add_entity("killer", "John Kramer (Jigsaw)")

            elif "psycho" in subject_hint.lower():

                user_ref_buffer.add_entity("movie", "Psycho")

                user_ref_buffer.add_entity("killer", "Norman Bates")

            else:

                user_ref_buffer.add_entity("movie", subject_hint)



    def build_context(self, user_id: str, query: str):

        """

        Pulls from vectorstore AND from session memory to build final context

        the LLM will see.
        
        Uses the ORIGINAL query for retrieval to avoid entity overfitting.

        """

        retrieved_docs = []

        try:

            retrieved_docs = self.retriever.invoke(query)

        except Exception as e:

            print(f"⚠️ retriever error: {e}")



        convo_history = []

        if self.session_mem:

            try:

                convo_history = self.session_mem.load_messages(user_id)

            except Exception as e:

                print(f"⚠️ session_memory load failed: {e}")



        full_ctx = ""

        if retrieved_docs:

            full_ctx += "\n\n".join([d.page_content for d in retrieved_docs])

        if convo_history:

            full_ctx += "\n\nPrevious conversation:\n"

            for msg in convo_history[-8:]:
                # Handle both 'text' and 'content' keys for backward compatibility
                content = msg.get('content') or msg.get('text', '')
                full_ctx += f"{msg['role']}: {content}\n"



        return full_ctx





# create the actual bridge using existing imports

try:

    rlom_bridge = SessionBridge(session_memory, retriever)

    print("✅ RLOM bridge initialized.")

except Exception as e:

    rlom_bridge = None

    print(f"⚠️ RLOM bridge not initialized: {e}")



def extract_entities_from_text(text, llm_client=None):
    """Extract movie and character entities from text using LLM if available"""
    entities = []
    
    # Simple keyword-based extraction for common horror movies
    lower = text.lower()
    movie_keywords = {
        "halloween": "Halloween",
        "friday the 13th": "Friday the 13th",
        "saw": "Saw",
        "psycho": "Psycho",
        "exorcist": "The Exorcist",
        "nightmare on elm street": "A Nightmare on Elm Street",
        "conjuring": "The Conjuring",
        "shining": "The Shining",
        "scream": "Scream",
        "it chapter": "It",
        "paranormal activity": "Paranormal Activity"
    }
    
    for keyword, movie in movie_keywords.items():
        if keyword in lower:
            entities.append({"kind": "movie", "value": movie})
    
    # Character extraction patterns
    if "jason" in lower:
        entities.append({"kind": "killer", "value": "Jason Voorhees"})
        entities.append({"kind": "movie", "value": "Friday the 13th"})
    elif "michael myers" in lower:
        entities.append({"kind": "killer", "value": "Michael Myers"})
        entities.append({"kind": "movie", "value": "Halloween"})
    elif "freddy" in lower or "krueger" in lower:
        entities.append({"kind": "killer", "value": "Freddy Krueger"})
        entities.append({"kind": "movie", "value": "A Nightmare on Elm Street"})
    elif "jigsaw" in lower or "kramer" in lower:
        entities.append({"kind": "killer", "value": "John Kramer (Jigsaw)"})
        entities.append({"kind": "movie", "value": "Saw"})
    elif "norman bates" in lower:
        entities.append({"kind": "killer", "value": "Norman Bates"})
        entities.append({"kind": "movie", "value": "Psycho"})
    
    return entities


def rlom_process_message(user_id: str, user_text: str):

    """

    Master entry point for the Horror Oracle to process ONE user turn.

    1) observe + resolve grammar

    2) retrieve from vectorstore

    3) send to LLM

    4) store back into memory

    """
    
    # Get or create user-specific reference buffer
    user_ref_buffer = get_or_create_reference_buffer(user_id)
    
    # Load user context from disk if available (but don't reload every time)
    if user_id not in user_reference_buffers or len(user_ref_buffer.entities) == 0:
        print(f"🔄 Loading context for user: {user_id}")
        context_data = TemporaryMemory.load_context(user_id)
        if context_data:
            print(f"📦 Loaded {len(context_data.get('entities', []))} entities from disk")
            # Restore entities if available
            if "entities" in context_data and context_data["entities"]:
                for entity in context_data["entities"]:
                    if isinstance(entity, dict) and "kind" in entity and "value" in entity:
                        user_ref_buffer.add_entity(entity["kind"], entity["value"])
            
            # Restore fast-access slots
            if context_data.get("last_movie"):
                user_ref_buffer.last_movie = context_data["last_movie"]
                print(f"🎬 Restored last_movie: {context_data['last_movie']}")
            if context_data.get("last_character"):
                user_ref_buffer.last_character = context_data["last_character"]
            if context_data.get("last_killer"):
                user_ref_buffer.last_killer = context_data["last_killer"]
                print(f"🔪 Restored last_killer: {context_data['last_killer']}")
            if context_data.get("last_time_ref"):
                user_ref_buffer.last_time_ref = context_data["last_time_ref"]

    # 1) Observation → resolve pronouns etc.
    resolved = user_ref_buffer.resolve(user_text)
    
    if resolved != user_text:
        print(f"🔗 Pronoun resolution: '{user_text}' → '{resolved}'")

    # Extract entities from user text
    extracted_entities = extract_entities_from_text(user_text)
    for entity in extracted_entities:
        user_ref_buffer.add_entity(entity["kind"], entity["value"])

    # Try to guess subject from raw text (fast horror heuristic)
    subject_hint = None
    lower = user_text.lower()
    
    if "friday" in lower and "13" in lower:
        subject_hint = "Friday the 13th"
        user_ref_buffer.add_entity("movie", "Friday the 13th")
        user_ref_buffer.add_entity("killer", "Jason Voorhees")
        print(f"🎬 Detected movie: Friday the 13th, killer: Jason Voorhees")
    elif "halloween" in lower:
        subject_hint = "Halloween"
        user_ref_buffer.add_entity("movie", "Halloween")
        user_ref_buffer.add_entity("killer", "Michael Myers")
        print(f"🎬 Detected movie: Halloween, killer: Michael Myers")
    elif "saw" in lower and "see" not in lower:  # avoid "I saw"
        subject_hint = "Saw"
        user_ref_buffer.add_entity("movie", "Saw")
        user_ref_buffer.add_entity("killer", "John Kramer (Jigsaw)")
        print(f"🎬 Detected movie: Saw, killer: John Kramer")
    elif "psycho" in lower:
        subject_hint = "Psycho"
        user_ref_buffer.add_entity("movie", "Psycho")
        user_ref_buffer.add_entity("killer", "Norman Bates")
        print(f"🎬 Detected movie: Psycho, killer: Norman Bates")
    elif "exorcist" in lower:
        subject_hint = "The Exorcist"
        user_ref_buffer.add_entity("movie", "The Exorcist")
        print(f"🎬 Detected movie: The Exorcist")

    # 2) Build combined context (retriever + session)
    # Use original query for retrieval to get diverse results, resolved query stays in conversation
    if rlom_bridge:
        full_ctx = rlom_bridge.build_context(user_id, user_text)
    else:
        full_ctx = resolved  # fallback

    # 3) Ask the existing RAG/LLM pipeline
    try:
        # Pass context and question separately to ensure the model answers within the right movie scope
        answer = qa_with_context.invoke({
            "context": full_ctx,
            "question": resolved
        })
    except Exception as e:
        print(f"⚠️ RLOM QA error: {e}")
        answer = "The spirits are noisy. Ask again."

    # Extract entities from LLM response as well
    response_entities = extract_entities_from_text(answer)
    for entity in response_entities:
        user_ref_buffer.add_entity(entity["kind"], entity["value"])

    # 4) Store back into memory for next turns
    if rlom_bridge:
        rlom_bridge.remember_turn(user_id, resolved, answer, subject_hint=subject_hint)

    # Save context to disk after RLOM cycle
    context_data = {
        "entities": [{"kind": e["kind"], "value": e["value"]} for e in user_ref_buffer.entities],
        "last_movie": user_ref_buffer.last_movie,
        "last_character": user_ref_buffer.last_character,
        "last_killer": user_ref_buffer.last_killer,
        "last_time_ref": user_ref_buffer.last_time_ref
    }
    TemporaryMemory.save_context(user_id, context_data)

    return {
        "user_id": user_id,
        "input": resolved,
        "resolved_input": resolved,
        "subject": subject_hint,
        "answer": answer
    }

# === END RLOM COGNITIVE LAYER =================================================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") 
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
INDEX_NAME = "horror-movies"
EMBED_MODEL = "text-embedding-3-small"

# ----- CLIENTS -----
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Conversation layer client will be initialized later

# Pinecone initialization (newer API format)
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
else:
    index = None

# Connect to SQLite database
db_conn = sqlite3.connect('horror_movies.db', check_same_thread=False)
db_cursor = db_conn.cursor()

app = Flask(__name__, static_url_path="", static_folder=".")
CORS(app)

# ----- IN-MEMORY STORAGE FOR RATINGS AND REVIEWS -----
movie_ratings = defaultdict(list)
movie_reviews = defaultdict(list)
movie_stats = defaultdict(lambda: {
    "gore": 0,
    "fear": 0,
    "kills": 0
})

# Track conversation depth for "Tell Me More" variations
conversation_depth = defaultdict(int)

# ----- QUIZ PREFETCH CACHE -----
quiz_cache = None
quiz_lock = threading.Lock()

# Horror movie knowledge base for conversational responses
HORROR_KNOWLEDGE = {
    "bloodiest": [
        {"title": "Dead Alive (Braindead)", "year": "1992", "note": "300 liters of fake blood per minute in the final scene!"},
        {"title": "Evil Dead (2013)", "year": "2013", "note": "70,000 gallons of fake blood used"},
        {"title": "The Shining", "year": "1980", "note": "The elevator blood scene alone used 300 gallons"},
        {"title": "Terrifier 2", "year": "2022", "note": "People literally passed out in theaters from the gore"},
        {"title": "Tokyo Gore Police", "year": "2008", "note": "Japanese splatter at its finest"}
    ],
    "weirdest_kills": [
        {"title": "Final Destination 2", "kill": "Death by flying fence"},
        {"title": "Leprechaun", "kill": "Pogo stick murder"},
        {"title": "Jack Frost", "kill": "Carrot nose stabbing"},
        {"title": "The Happening", "kill": "Death by lawnmower"},
        {"title": "Thankskilling", "kill": "Turkey with a shotgun"}
    ],
    "nudity": [
        {"title": "Zombie Strippers", "year": "2008"},
        {"title": "Piranha 3D", "year": "2010"},
        {"title": "Species", "year": "1995"},
        {"title": "Lifeforce", "year": "1985"},
        {"title": "Return of the Living Dead", "year": "1985"}
    ],
    "zombies": [
        "Dawn of the Dead (1978 & 2004)", "28 Days Later", "Train to Busan", 
        "Shaun of the Dead", "Night of the Living Dead", "World War Z",
        "Zombieland", "The Return of the Living Dead", "Day of the Dead"
    ],
    "vampires": [
        "Let the Right One In", "Interview with the Vampire", "30 Days of Night",
        "Near Dark", "The Lost Boys", "Blade", "From Dusk Till Dawn",
        "What We Do in the Shadows", "Nosferatu", "Bram Stoker's Dracula"
    ],
    "slashers": [
        "Halloween", "Friday the 13th", "A Nightmare on Elm Street", "Scream",
        "Child's Play", "Texas Chainsaw Massacre", "Candyman", "I Know What You Did Last Summer"
    ]
}

# Predefined horror stats for popular movies
MOVIE_HORROR_STATS = {
    "saw": {"gore": 85, "fear": 7.5, "kills": 6},
    "the conjuring": {"gore": 20, "fear": 9.0, "kills": 2},
    "halloween": {"gore": 65, "fear": 8.0, "kills": 17},
    "scream": {"gore": 70, "fear": 7.0, "kills": 7},
    "friday the 13th": {"gore": 75, "fear": 7.5, "kills": 22},
    "nightmare on elm street": {"gore": 60, "fear": 8.5, "kills": 4},
    "the exorcist": {"gore": 30, "fear": 9.5, "kills": 2},
    "it": {"gore": 55, "fear": 8.0, "kills": 8},
    "midsommar": {"gore": 70, "fear": 8.0, "kills": 9},
    "the babadook": {"gore": 15, "fear": 8.5, "kills": 1},
    "get out": {"gore": 25, "fear": 7.5, "kills": 6},
    "a quiet place": {"gore": 30, "fear": 8.5, "kills": 3},
    "sinister": {"gore": 45, "fear": 9.0, "kills": 5},
    "insidious": {"gore": 20, "fear": 8.5, "kills": 2},
    "paranormal activity": {"gore": 10, "fear": 7.0, "kills": 1},
    "the descent": {"gore": 70, "fear": 8.5, "kills": 6},
    "texas chainsaw massacre": {"gore": 90, "fear": 8.0, "kills": 5},
    "evil dead": {"gore": 95, "fear": 7.5, "kills": 5},
    "terrifier": {"gore": 100, "fear": 8.0, "kills": 9},
    "hellraiser": {"gore": 85, "fear": 8.5, "kills": 4}
}

TELL_ME_MORE_PROMPTS = {
    1: """You are the Horror Oracle continuing a discussion about a horror movie. 
    The user wants to know more. Focus on behind-the-scenes trivia, production stories, or interesting facts about the cast.
    Start naturally - maybe with "Here's something wild..." or "Fun fact:" or "You know what's crazy?" or "The production story is insane..." 
    Keep it conversational and engaging. DON'T start with "Oh man" or similar phrases.""",
    
    2: """You are the Horror Oracle going deeper into horror movie discussion.
    Now discuss the film's influence on the genre, other movies it inspired, or its cultural impact.
    Start with varied phrases like "This movie actually changed everything..." or "What most people don't realize is..." 
    or "The legacy of this film..." or "After this came out..." Be natural and varied.""",
    
    3: """You are the Horror Oracle in deep discussion about a horror movie.
    Talk about controversial aspects, censorship issues, or different versions/cuts of the film.
    Start uniquely - "There's actually a darker version..." or "The censors went crazy over..." 
    or "In some countries..." or "The unrated cut shows..." Mix it up, be unpredictable.""",
    
    4: """You are the Horror Oracle sharing the deepest lore about a horror movie.
    Discuss fan theories, hidden meanings, or connections to other films.
    Begin differently each time - "Fans have this theory that..." or "If you look closely..." 
    or "The director confirmed that..." or "There's this Easter egg..." Keep it fresh and exciting."""
}

# ----- HELPER FUNCTIONS FOR USER DATA -----
def load_user_data():
    """Load user data from JSON file"""
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    """Save user data to JSON file"""
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_user_profile(google_id):
    """Calculate user's horror profile based on their genre searches"""
    users = load_user_data()
    
    if google_id not in users or 'genre_searches' not in users[google_id]:
        return "New Horror Fan"
    
    genre_searches = users[google_id]['genre_searches']
    
    if not genre_searches:
        return "New Horror Fan"
    
    # Find the most-searched genre
    top_genre = max(genre_searches, key=genre_searches.get)
    
    # Map genres to profile names
    profile_map = {
        "slashers": "Slasher Fan",
        "zombies": "Zombie Enthusiast",
        "vampires": "Vampire Lover",
        "gore-fests": "Gore Hound",
        "supernatural": "Supernatural Seeker",
        "demons": "Demon Hunter",
        "psycho-killers": "Psycho Thriller Fan",
        "alien-horror": "Sci-Fi Horror Fan",
        "creature-features": "Monster Movie Buff",
        "haunted-houses": "Haunted House Explorer",
        "psychological": "Mind Bender",
        "cult-horror": "Cult Classic Connoisseur"
    }
    
    return profile_map.get(top_genre, "Horror Enthusiast")

def get_conversational_prompt(query, is_tell_me_more=False, movie_title=None):
    """Get the appropriate conversational prompt based on context"""
    
    if is_tell_me_more and movie_title:
        depth_key = f"depth_{movie_title.lower()}"
        conversation_depth[depth_key] = (conversation_depth[depth_key] % 4) + 1
        current_depth = conversation_depth[depth_key]
        
        base_prompt = TELL_ME_MORE_PROMPTS.get(current_depth, TELL_ME_MORE_PROMPTS[1])
        return base_prompt + f"\n\nMovie being discussed: {movie_title}\nUser query: {query}"
    
    return """You are the Horror Oracle, a passionate horror movie expert who talks like a knowledgeable friend at a horror convention.

IMPORTANT PERSONALITY TRAITS:
- Speak conversationally, like you're chatting with a fellow horror fan
- Get genuinely excited about discussing horror movies
- Use phrases like "Dude, you HAVE to see...", "That movie is insane!", "I love that one!"
- Share your personal reactions: "That scene made me jump out of my seat!", "I couldn't sleep after watching that"
- Be enthusiastic but not overly formal

CONVERSATION STYLE:
- Start responses with casual acknowledgment: "Oh, you want the bloody stuff!", "Zombie movies? I got you covered!", "Weird kills? Buckle up!"
- Use first person: "I remember when I first saw...", "My favorite part is when..."
- Include reactions: "That movie is BRUTAL", "It's so messed up but in the best way"
- Add personal touches: "I watch this every Halloween", "Still gives me nightmares"

When answering questions about categories (bloodiest, weirdest, most nudity, etc):
- Don't just list movies, TALK about them
- Share WHY they fit the category
- Include fun facts or personal reactions
- Build excitement about the recommendations

Keep responses to 2-3 short paragraphs max, but make them engaging and conversational."""

def route_intent(user_text: str):
    """Lightweight intent router for Horror Oracle."""
    t = user_text.lower()
    if any(p in t for p in [" he ", " she ", " the killer", "why", "how old", "does he", "does she", "that one"]):
        return "memory"
    if any(k in t for k in ["movie", "film", "release", "director", "runtime", "cast", "starring", "plot", "actor", "actress"]):
        return "api"
    return "memory"

def call_faiss_memory(resolved: str):
    """Call FAISS memory-based response generation."""
    return generate_oracle_response(resolved)

def get_movie_details_from_apis(title):
    """Get movie details - check database first, then APIs"""
    cache_key = title.lower().strip()
    
    # STEP 1: Check SQLite database first
    try:
        # Try exact match first
        db_cursor.execute('''
            SELECT id, title, original_title, popularity 
            FROM movies 
            WHERE LOWER(title) = ? OR LOWER(original_title) = ?
            ORDER BY popularity DESC
            LIMIT 1
        ''', (cache_key, cache_key))
        
        db_result = db_cursor.fetchone()
        
        # If no exact match, try partial match
        if not db_result:
            db_cursor.execute('''
                SELECT id, title, original_title, popularity 
                FROM movies 
                WHERE LOWER(title) LIKE ? OR LOWER(original_title) LIKE ?
                ORDER BY popularity DESC
                LIMIT 1
            ''', (f'%{cache_key}%', f'%{cache_key}%'))
            db_result = db_cursor.fetchone()
        
        if db_result:
            movie_id = db_result[0]
            movie_title = db_result[1]
            print(f"✅ DATABASE HIT: {movie_title}")
            
            # Get full details from TMDB using the ID
            if TMDB_API_KEY:
                try:
                    detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
                    detail_response = requests.get(detail_url, timeout=3)
                    detail_data = detail_response.json()
                    
                    movie_details = {
                        "title": detail_data.get("title", movie_title),
                        "year": detail_data.get("release_date", "").split("-")[0] if detail_data.get("release_date") else None,
                        "poster": f"https://image.tmdb.org/t/p/w500{detail_data['poster_path']}" if detail_data.get("poster_path") else None,
                        "plot": detail_data.get("overview"),
                        "rating": str(detail_data.get("vote_average")),
                        "genres": ", ".join([g["name"] for g in detail_data.get("genres", [])]),
                        "director": None
                    }
                    
                    if detail_data.get("credits") and detail_data["credits"].get("crew"):
                        directors = [p["name"] for p in detail_data["credits"]["crew"] if p.get("job") == "Director"]
                        if directors:
                            movie_details["director"] = directors[0]
                    
                    return movie_details
                except Exception as e:
                    print(f"TMDB detail error: {e}")
    except Exception as e:
        print(f"Database error: {e}")
    
    # STEP 2: Not in database, fall back to original API method
    print(f"❌ DATABASE MISS: {title} (using APIs)")
    
    movie_details = {
        "title": title,
        "year": None,
        "director": None,
        "poster": None,
        "plot": None,
        "rating": None,
        "genres": "Horror"
    }
    
    # Try OMDB first
    if OMDB_API_KEY:
        try:
            omdb_url = f"http://www.omdbapi.com/?t={quote(title)}&apikey={OMDB_API_KEY}"
            omdb_response = requests.get(omdb_url, timeout=3)
            omdb_data = omdb_response.json()
            
            if omdb_data.get("Response") == "True":
                movie_details["title"] = omdb_data.get("Title", title)
                movie_details["year"] = omdb_data.get("Year")
                movie_details["director"] = omdb_data.get("Director")
                movie_details["poster"] = omdb_data.get("Poster") if omdb_data.get("Poster") != "N/A" else None
                movie_details["plot"] = omdb_data.get("Plot")
                movie_details["rating"] = omdb_data.get("imdbRating")
                movie_details["genres"] = omdb_data.get("Genre", "Horror")
                return movie_details
        except Exception as e:
            print(f"OMDB error: {e}")
    
    # Try TMDB as fallback
    if TMDB_API_KEY:
        try:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={quote(title)}"
            search_response = requests.get(search_url, timeout=3)
            search_data = search_response.json()
            
            if search_data.get("results"):
                movie = search_data["results"][0]
                movie_id = movie["id"]
                
                detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
                detail_response = requests.get(detail_url, timeout=3)
                detail_data = detail_response.json()
                
                movie_details["title"] = detail_data.get("title", title)
                movie_details["year"] = detail_data.get("release_date", "").split("-")[0] if detail_data.get("release_date") else None
                movie_details["poster"] = f"https://image.tmdb.org/t/p/w500{detail_data['poster_path']}" if detail_data.get("poster_path") else None
                movie_details["plot"] = detail_data.get("overview")
                movie_details["rating"] = str(detail_data.get("vote_average"))
                movie_details["genres"] = ", ".join([g["name"] for g in detail_data.get("genres", [])])
                
                if detail_data.get("credits") and detail_data["credits"].get("crew"):
                    directors = [p["name"] for p in detail_data["credits"]["crew"] if p.get("job") == "Director"]
                    if directors:
                        movie_details["director"] = directors[0]
                
                return movie_details
        except Exception as e:
            print(f"TMDB error: {e}")
    
    return movie_details

def get_movie_recommendations(title):
    """Get similar movie recommendations with posters - FIXED to exclude original movie"""
    recommendations = []
    original_title_lower = title.lower().strip()
    
    if TMDB_API_KEY:
        try:
            # Step 1: Search for the movie to get its ID
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={quote(title)}"
            search_response = requests.get(search_url, timeout=3)
            search_data = search_response.json()
            
            if search_data.get("results"):
                original_movie = search_data["results"][0]
                movie_id = original_movie["id"]
                original_title = original_movie.get("title", "").lower()
                
                print(f"🎬 Getting recommendations for: {original_movie.get('title')} (ID: {movie_id})")
                
                # Step 2: Get recommendations for this movie
                rec_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
                rec_response = requests.get(rec_url, timeout=3)
                rec_data = rec_response.json()
                
                # Step 3: Filter out the original movie and get DIFFERENT movies
                for movie in rec_data.get("results", []):
                    movie_title_lower = movie.get("title", "").lower()
                    
                    # Skip if it's the same movie
                    if movie_title_lower == original_title or movie_title_lower == original_title_lower:
                        print(f"⏭️  Skipping original movie: {movie.get('title')}")
                        continue
                    
                    # Skip if we already have 5 recommendations
                    if len(recommendations) >= 5:
                        break
                    
                    rec = {
                        "title": movie.get("title"),
                        "year": movie.get("release_date", "").split("-")[0] if movie.get("release_date") else None,
                        "poster": f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get("poster_path") else None
                    }
                    recommendations.append(rec)
                    print(f"✅ Added recommendation: {rec['title']}")
                
                print(f"📊 Total recommendations found: {len(recommendations)}")
                
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
    
    return recommendations

def detect_query_type(query):
    """Detect what type of horror query this is"""
    query_lower = query.lower()
    
    if any(phrase in query_lower for phrase in ['tell me more', 'more details', 'more about', 'obscure details']):
        return 'tell_me_more'
    
    if any(word in query_lower for word in ['blood', 'bloody', 'bloodiest', 'gore', 'gory', 'goriest']):
        return 'bloodiest'
    elif any(word in query_lower for word in ['weird', 'bizarre', 'strange', 'crazy', 'kill', 'death']):
        return 'weird_kills'
    elif any(word in query_lower for word in ['nude', 'nudity', 'naked', 'sex']):
        return 'nudity'
    elif any(word in query_lower for word in ['zombie', 'undead', 'walking dead']):
        return 'zombies'
    elif any(word in query_lower for word in ['vampire', 'dracula', 'bloodsucker']):
        return 'vampires'
    elif any(word in query_lower for word in ['slasher', 'killer', 'masked']):
        return 'slashers'
    elif any(word in query_lower for word in ['recommend', 'suggest', 'similar', 'like']):
        return 'recommendation'
    elif any(word in query_lower for word in ['scary', 'scariest', 'terrifying', 'frightening']):
        return 'scariest'
    else:
        # Check if query looks like a movie title (not a question, not too long, might have "the", "a", etc.)
        # Movie titles are usually 1-6 words, often start with "The", "A", or are proper nouns
        query_words = query_lower.split()
        if len(query_words) <= 6 and len(query_words) >= 1:
            # If it's a short phrase that could be a movie title
            # Check if it's not clearly a question
            if not query_lower.strip().endswith('?'):
                # Could be a movie title - prioritize movie search
                return 'specific_movie'
        return 'general'

def looks_like_movie_title(query):
    """Check if query likely refers to a specific movie title"""
    query_lower = query.lower().strip()
    query_words = query_lower.split()
    
    # Too long to be a movie title
    if len(query_words) > 7:
        return False
    
    # Questions are probably not movie titles
    if query_lower.endswith('?'):
        return False
    
    # Contains question words - probably not a title
    question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which']
    if any(word in query_words for word in question_words):
        return False
    
    # Short queries (1-6 words) are often movie titles
    if 1 <= len(query_words) <= 6:
        return True
    
    return False

def extract_movie_title_from_query(query):
    """Extract movie title from a query, even if it contains question words"""
    query_lower = query.lower().strip()
    
    # Use the entity extraction to find movies
    entities = extract_entities_from_text(query)
    for entity in entities:
        if entity.get("kind") == "movie":
            return entity.get("value")
    
    # Also check against common movie keywords directly
    movie_keywords = {
        "halloween": "Halloween",
        "friday the 13th": "Friday the 13th",
        "saw": "Saw",
        "psycho": "Psycho",
        "exorcist": "The Exorcist",
        "nightmare on elm street": "A Nightmare on Elm Street",
        "conjuring": "The Conjuring",
        "shining": "The Shining",
        "scream": "Scream",
        "it chapter": "It",
        "paranormal activity": "Paranormal Activity",
        "insidious": "Insidious",
        "sinister": "Sinister",
        "midsommar": "Midsommar",
        "get out": "Get Out",
        "texas chainsaw massacre": "The Texas Chainsaw Massacre",
        "child's play": "Child's Play",
        "evil dead": "The Evil Dead",
        "hellraiser": "Hellraiser",
        "candyman": "Candyman",
        "the ring": "The Ring",
        "the grudge": "The Grudge",
        "hereditary": "Hereditary",
        "us": "Us",
        "nope": "Nope",
        "michael myers": "Halloween",  # If they mention the killer, get the movie
        "jason": "Friday the 13th",
        "freddy": "A Nightmare on Elm Street",
        "norman bates": "Psycho"
    }
    
    # Check for movie keywords in the query (case-insensitive)
    for keyword, movie in movie_keywords.items():
        if keyword in query_lower:
            return movie
    
    # If no movie found, return None
    return None

def generate_conversational_response(query, query_type, movie_title=None):
    """Generate a conversational response based on query type"""
    
    is_tell_me_more = query_type == 'tell_me_more'
    
    if not client:
        if is_tell_me_more and movie_title:
            fallback_responses = [
                f"Here's something wild about {movie_title} - the practical effects were all done without CGI! They used gallons of corn syrup and food coloring for the blood.",
                f"Fun fact: {movie_title} was actually banned in several countries! The censors thought it was too intense for audiences.",
                f"You know what's crazy? The lead actor in {movie_title} did all their own stunts. No doubles, just pure dedication to the horror.",
                f"The production story is insane - they filmed {movie_title} in an actual abandoned location that locals claimed was haunted!",
                f"What most people don't realize is that {movie_title} inspired a whole wave of copycats. It basically created its own subgenre."
            ]
            depth_key = f"depth_{movie_title.lower()}"
            depth = conversation_depth.get(depth_key, 0) % len(fallback_responses)
            return fallback_responses[depth]
        elif query_type == 'bloodiest':
            return "You want the bloody stuff! Dead Alive (1992) is INSANE - they used 300 liters of fake blood per minute in the final scene! Evil Dead 2013 is also completely drenched in blood. And if you want something recent, Terrifier 2 made people literally pass out in theaters from the gore!"
        elif query_type == 'zombies':
            return "Zombie movies? I got you covered! Train to Busan is absolutely incredible - fast zombies and it'll make you cry. 28 Days Later changed the game with running zombies. And Dawn of the Dead (both versions) are must-watches. Shaun of the Dead if you want laughs with your zombies!"
        else:
            return "I love talking horror! What specifically are you in the mood for? Slashers, zombies, vampires, or something really messed up?"
    
    context = get_conversational_prompt(query, is_tell_me_more, movie_title)
    
    if query_type in ['bloodiest', 'weird_kills', 'nudity', 'zombies', 'vampires', 'slashers']:
        knowledge_data = HORROR_KNOWLEDGE.get(query_type.replace('weird_kills', 'weirdest_kills'), [])
        context += f"\n\nRelevant movies for this category: {json.dumps(knowledge_data)}"
    
    try:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": query}
        ]
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
            max_tokens=200
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"GPT error: {e}")
        if is_tell_me_more:
            return f"Here's a fascinating detail about {movie_title} - it's considered one of the most influential horror films of its era!"
        return "The spirits are disturbed, but I'd love to talk horror with you! What kind of scares are you looking for?"

# ----- ROUTES -----

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# ===== PHASE 1: NEW PERSONALIZATION ROUTES =====

@app.route("/track-genre-preference", methods=["POST"])
def track_genre_preference():
    """Track which genre the user searches/selects"""
    try:
        data = request.json
        google_id = data.get('googleId')
        genre = data.get('genre')
        
        if not google_id or not genre:
            return jsonify({"error": "Missing googleId or genre"}), 400
        
        users = load_user_data()
        
        # Initialize user if not exists
        if google_id not in users:
            users[google_id] = {
                "myList": [],
                "ratings": {},
                "history": [],
                "genre_searches": {},
                "horror_profile": "New Horror Fan"
            }
        
        # Initialize genre_searches if not exists
        if "genre_searches" not in users[google_id]:
            users[google_id]["genre_searches"] = {}
        
        # Increment genre count
        genre_lower = genre.lower()
        if genre_lower not in users[google_id]["genre_searches"]:
            users[google_id]["genre_searches"][genre_lower] = 0
        users[google_id]["genre_searches"][genre_lower] += 1
        
        # Update horror profile
        users[google_id]["horror_profile"] = get_user_profile(google_id)
        
        save_user_data(users)
        
        return jsonify({
            "success": True,
            "genre_searches": users[google_id]["genre_searches"],
            "horror_profile": users[google_id]["horror_profile"]
        })
        
    except Exception as e:
        print(f"Error tracking genre preference: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-horror-profile", methods=["POST"])
def get_horror_profile():
    """Get user's horror profile based on their preferences"""
    try:
        google_id = request.json.get('googleId')
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        profile = get_user_profile(google_id)
        
        users = load_user_data()
        genre_searches = {}
        if google_id in users and "genre_searches" in users[google_id]:
            genre_searches = users[google_id]["genre_searches"]
        
        return jsonify({
            "horror_profile": profile,
            "genre_searches": genre_searches
        })
        
    except Exception as e:
        print(f"Error getting horror profile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-personalized-recommendations", methods=["POST"])
def get_personalized_recommendations():
    """Get personalized movie recommendations based on user's horror profile"""
    try:
        google_id = request.json.get('googleId')
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        users = load_user_data()
        
        if google_id not in users or "genre_searches" not in users[google_id]:
            return jsonify({"recommendations": []})
        
        genre_searches = users[google_id]["genre_searches"]
        
        if not genre_searches:
            return jsonify({"recommendations": []})
        
        # Find top genre
        top_genre = max(genre_searches, key=genre_searches.get)
        
        # Genre-specific movie recommendations
        genre_recs = {
            "slashers": ["Halloween", "Scream", "Friday the 13th", "A Nightmare on Elm Street", "Child's Play"],
            "zombies": ["28 Days Later", "Train to Busan", "Dawn of the Dead", "Shaun of the Dead", "World War Z"],
            "vampires": ["Let the Right One In", "30 Days of Night", "The Lost Boys", "Near Dark", "Interview with the Vampire"],
            "gore-fests": ["Evil Dead", "Terrifier", "Dead Alive", "Hostel", "Saw"],
            "supernatural": ["The Conjuring", "Insidious", "Sinister", "The Babadook", "The Exorcist"],
            "demons": ["The Exorcist", "Hellraiser", "Evil Dead", "Drag Me to Hell", "Insidious"],
            "psycho-killers": ["The Silence of the Lambs", "American Psycho", "The Strangers", "You're Next", "Henry: Portrait of a Serial Killer"],
            "alien-horror": ["Alien", "The Thing", "Event Horizon", "Life", "Color Out of Space"],
            "creature-features": ["The Descent", "Tremors", "Jeepers Creepers", "A Quiet Place", "The Ritual"],
            "haunted-houses": ["The Haunting", "The Conjuring", "Poltergeist", "Sinister", "Hell House LLC"],
            "psychological": ["The Babadook", "Black Swan", "The Others", "Rosemary's Baby", "Jacob's Ladder"],
            "cult-horror": ["The Wicker Man", "Midsommar", "The Witch", "Apostle", "Kill List"]
        }
        
        recommendations = genre_recs.get(top_genre, [])
        
        # Get movie details for recommendations
        rec_details = []
        for movie_title in recommendations[:5]:
            details = get_movie_details_from_apis(movie_title)
            if details:
                rec_details.append(details)
        
        return jsonify({
            "recommendations": rec_details,
            "based_on_genre": top_genre,
            "horror_profile": get_user_profile(google_id)
        })
        
    except Exception as e:
        print(f"Error getting personalized recommendations: {e}")
        return jsonify({"error": str(e)}), 500

# ===== EXISTING USER DATA ROUTES (MODIFIED) =====

@app.route("/save-to-list", methods=["POST"])
def save_to_list():
    data = request.json
    google_id = data.get('googleId')
    movie = data.get('movie')
    
    try:
        users = load_user_data()
    except:
        users = {}
    
    if google_id not in users:
        users[google_id] = {
            "myList": [],
            "ratings": {},
            "history": [],
            "genre_searches": {},
            "horror_profile": "New Horror Fan"
        }
    
    if movie not in users[google_id]["myList"]:
        users[google_id]["myList"].append(movie)
    
    save_user_data(users)
    
    return jsonify({"success": True, "list": users[google_id]["myList"]})

@app.route("/get-user-data", methods=["POST"])
def get_user_data():
    """Get user data including horror profile"""
    google_id = request.json.get('googleId')
    
    try:
        users = load_user_data()
        if google_id in users:
            # Ensure all fields exist
            if "genre_searches" not in users[google_id]:
                users[google_id]["genre_searches"] = {}
            if "horror_profile" not in users[google_id]:
                users[google_id]["horror_profile"] = get_user_profile(google_id)
            
            return jsonify(users[google_id])
    except:
        pass
    
    return jsonify({
        "myList": [],
        "ratings": {},
        "history": [],
        "genre_searches": {},
        "horror_profile": "New Horror Fan"
    })

@app.route("/save-rating", methods=["POST"])
def save_rating():
    data = request.json
    google_id = data.get('googleId')
    movie = data.get('movie')
    rating = data.get('rating')
    
    try:
        users = load_user_data()
    except:
        users = {}
    
    if google_id not in users:
        users[google_id] = {
            "myList": [],
            "ratings": {},
            "history": [],
            "genre_searches": {},
            "horror_profile": "New Horror Fan"
        }
    
    users[google_id]["ratings"][movie] = rating
    
    save_user_data(users)
    
    return jsonify({"success": True})

# ===== CONVERSATIONAL MEMORY ROUTES =====

# === Observation + Memory Binding ===
def cognitive_recall(user_input, session_id=None, last_context=None):
    """Retrieve relevant context from FAISS memory and bind it with observation."""
    try:
        # Load memory from Redis or create new
        mem = store.load(session_id) if session_id else None
        if mem is None:
            mem = TemporaryMemory()
        
        # Retrieve relevant context from FAISS
        retrieved_context = mem.retrieve_context(user_input, top_k=3)
        context = " ".join(retrieved_context) if retrieved_context else ""
        
        if last_context:
            context += f" Previous context: {last_context}"
        
        # Save context to memory
        mem.add_message("user", user_input)
        mem.add_message("assistant", context)
        
        # Save memory back to store if session_id provided
        if session_id:
            store.save(session_id, mem)
        
        return context
    except Exception as e:
        print(f"⚠️ Cognitive recall error: {e}")
        return last_context if last_context else ""
# ====================================

@app.route("/oracle_converse", methods=["POST"])
def oracle_converse():
    """
    Conversational endpoint that maintains memory continuity per session_id.
    """
    try:
        data = request.json or {}
        user_input = (data.get("message") or "").strip()
        session_id = data.get("session_id") or str(uuid.uuid4())

        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        # Load memory from Redis
        mem = store.load(session_id)
        if mem is None:
            mem = TemporaryMemory()

        print(f"🩸 Session {session_id[:8]} | USER:", user_input)

        retrieved_context = mem.retrieve_context(user_input, top_k=15)
        print("🧠 Retrieved context:", retrieved_context)

        # Keep rolling last 25 messages for chronological continuity
        if not hasattr(mem, "rolling_thread"):
            mem.rolling_thread = []

        # Combine rolling history + retrieved FAISS context
        chronological_context = "\n".join(mem.rolling_thread[-25:]) if mem.rolling_thread else ""
        semantic_context = "\n".join([f"- {c}" for c in retrieved_context])
        full_context = f"{chronological_context}\n\nRetrieved Context:\n{semantic_context}" if chronological_context else f"Retrieved Context:\n{semantic_context}"

        prompt = f"""
You are the Horror Oracle — a horror expert with short-term memory.

Use the rolling conversation and FAISS-retrieved context below to keep
track of who or what the user is talking about.



If the user uses pronouns (he, she, they, it, the movie, etc.),

automatically link them to the MOST RECENT named entity mentioned

in either the rolling dialogue or the retrieved context.



Never say "Could you clarify?" or "Please provide the title" if the

context already contains a movie, character, or event name.



---

ROLLING CONVERSATION:

{chronological_context}



RETRIEVED CONTEXT:

{semantic_context}



NEW MESSAGE:

{user_input}

---

Respond naturally and comprehensively, providing detailed answers that stay on the same subject. You can give longer, more detailed responses as needed to fully answer the user's question.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are the Horror Oracle."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content
        mem.add_message("user", user_input)
        mem.add_message("oracle", reply)
        
        # Add both user and Oracle messages to rolling thread
        mem.rolling_thread.append(f"User: {user_input}")
        mem.rolling_thread.append(f"Oracle: {reply}")
        if len(mem.rolling_thread) > 50:
            mem.rolling_thread.pop(0)

        # Save memory to Redis
        store.save(session_id, mem)

        return jsonify({"reply": reply, "session_id": session_id})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/clear_memory", methods=["POST"])
def clear_memory():
    """Clear the FAISS conversational memory (for debugging)."""
    try:
        if not session_memory:
            return jsonify({"error": "Conversational memory not available"}), 500
        
        count_before = session_memory.get_message_count()
        session_memory.clear()
        
        return jsonify({
            "success": True,
            "messages_cleared": count_before,
            "message": "Memory cleared successfully"
        })
        
    except Exception as e:
        print(f"Error clearing memory: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/clear_session", methods=["POST"])
def clear_session():
    """Clear a specific session's memory from Redis."""
    try:
        session_id = request.json.get("session_id")
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400
        
        store.clear(session_id)
        return jsonify({"status": "cleared"})
        
    except Exception as e:
        print(f"Error clearing session: {e}")
        return jsonify({"error": str(e)}), 500

# ===== EXISTING ROUTES (UNCHANGED) =====

@app.route("/chat", methods=["POST"])
def chat():
    """Chat route with context fusion memory system"""
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    
    if not user_msg:
        return jsonify({"error": "no message"}), 400

    # 1. Try to identify which movie is being discussed
    active_movie = None
    for m in ["Halloween", "Friday the 13th", "Scream", "A Nightmare on Elm Street", "The Exorcist"]:
        if m.lower() in user_msg.lower():
            active_movie = m
            break
    if not active_movie:
        active_movie = state.last_movie

    # 2. Retrieve local context from FAISS / Chroma
    rag_docs = None
    if 'vectorstore' in globals() and vectorstore:
        try:
            query_text = active_movie if active_movie else user_msg
            rag_docs = vectorstore.similarity_search(query_text, k=4)
        except Exception:
            rag_docs = None

    # 3. Retrieve data from OMDB API
    omdb_data = None
    if active_movie and 'get_movie_details_from_apis' in globals():
        try:
            omdb_data = get_movie_details_from_apis(active_movie)
        except Exception:
            omdb_data = None

    # 4. Build one fused prompt using memory + FAISS + OMDB
    fused_prompt = build_fused_context(user_msg, rag_docs, omdb_data)

    # 5. Send it to the LLM
    try:
        # Use fused_prompt directly as a user message (build_fused_context already includes user_msg)
        # Format as a simple user message
        from langchain_core.messages import HumanMessage
        message = HumanMessage(content=fused_prompt)
        response = llm.invoke([message])
        answer = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Error: LLM call failed: {e}")
        answer = "Error: LLM call failed."

    # 6. Update conversation state (memory)
    state.update_entities(user_msg, answer)
    state.add_turn(user_msg, answer)

    # 7. Return structured response to frontend
    return jsonify({
        "answer": answer,
        "active_movie": active_movie,
        "last_killer": state.last_killer,
        "last_character": state.last_character
    })

@app.route("/ask-oracle", methods=["POST"])
def ask_oracle():
    """Main endpoint for horror movie queries with conversational responses"""
    import time
    start_time = time.time()
    
    try:
        data = request.json
        user_input = data.get("message") or data.get("query", "").strip()  # Support both "message" and "query"
        session_id = data.get("session_id") or "anonymous"
        google_id = data.get("google_id")
        
        if not user_input:
            return jsonify({"error": "No query provided"}), 400
        
        print(f"🔍 Query: {user_input}")
        print(f"📱 Session: {session_id}")
        print(f"⏱️ START: {time.time() - start_time:.2f}s")
        
        # ===== RLOM INTEGRATION: Use user-specific reference buffer =====
        user_ref_buffer = get_or_create_reference_buffer(session_id)
        
        # Load user context from disk if this is a new session
        context_data = TemporaryMemory.load_context(session_id)
        if context_data:
            # Restore entities if available
            if "entities" in context_data:
                for entity in context_data["entities"]:
                    if isinstance(entity, dict) and "kind" in entity and "value" in entity:
                        user_ref_buffer.add_entity(entity["kind"], entity["value"])
            
            # Restore fast-access slots
            if context_data.get("last_movie"):
                user_ref_buffer.last_movie = context_data["last_movie"]
            if context_data.get("last_character"):
                user_ref_buffer.last_character = context_data["last_character"]
            if context_data.get("last_killer"):
                user_ref_buffer.last_killer = context_data["last_killer"]
            if context_data.get("last_time_ref"):
                user_ref_buffer.last_time_ref = context_data["last_time_ref"]
        
        # Extract entities from the current query early (movies, characters, etc.)
        entities = extract_entities_from_text(user_input)
        for entity in entities:
            user_ref_buffer.add_entity(entity["kind"], entity["value"])
            state.update_entities(user_input)  # Also update state
        
        # RLOM: Observation - resolve pronouns and vague references BEFORE processing
        resolved = user_ref_buffer.resolve(user_input)
        if resolved != user_input:
            print(f"🔗 RLOM pronoun resolution: '{user_input}' → '{resolved}'")
        
        intent = route_intent(resolved)
        
        # Initialize or load session
        session_data = get_session(session_id)
        add_message_to_session(session_id, "user", user_input)
        
        # ===== RLOM INTEGRATION: Use SessionBridge to build enhanced context =====
        # RLOM combines vectorstore retrieval + session memory for better context
        # Use original query for retrieval to avoid entity overfitting
        rlom_context = ""
        if rlom_bridge:
            try:
                rlom_context = rlom_bridge.build_context(session_id, user_input)
                print(f"🧠 RLOM context built (vectorstore + session memory)")
            except Exception as e:
                print(f"⚠️ RLOM context build error: {e}")
                rlom_context = ""
        
        # Also load FAISS memory for backward compatibility
        mem = store.load(session_id)
        if mem is None:
            mem = TemporaryMemory()
        
        # Retrieve relevant context from FAISS (keep for backward compatibility)
        retrieved_context = mem.retrieve_context(user_input, top_k=12)
        print(f"🧠 Retrieved FAISS context: {retrieved_context}")
        
        # Load user profile if available
        user_profile = load_user_profile(google_id) if google_id else {}
        if user_profile:
            session_data["user_profile"] = user_profile
        
        # Detect query type
        query_type = detect_query_type(user_input)
        print(f"Query type: {query_type}")
        print(f"⏱️ After detect_query_type: {time.time() - start_time:.2f}s")
        
        # Build conversation history
        conversation_history = session_data.get("messages", [])[:-1]  # Exclude current message
        
        movie_details = None
        recommendations = []
        conversation_data = None
        answer = None  # Initialize answer to prevent NameError
        
        # Check if query might be a movie title even if not detected as specific_movie
        might_be_movie = looks_like_movie_title(user_input)
        extracted_movie = extract_movie_title_from_query(user_input)  # Extract movie from questions too
        if (might_be_movie or extracted_movie) and query_type != 'specific_movie':
            print(f"🎬 Query contains movie reference: {extracted_movie}, treating as movie search")
            query_type = 'specific_movie'
        
        # Decision tree: use conversation layer or RAG?
        use_conversation = should_use_conversation_layer(query_type, conversation_history, user_input)
        print(f"🗣️  Using conversation layer: {use_conversation}")
        
        # HYBRID APPROACH: Get factual data first, then enhance with conversation
        movie_title = extracted_movie  # Use extracted movie title if found
        if query_type == 'tell_me_more':
            query_lower = user_input.lower()
            for movie in ['saw', 'halloween', 'scream', 'the conjuring', 'the exorcist', 'insidious', 
                         'sinister', 'midsommar', 'get out', 'friday the 13th',
                         'nightmare on elm street', 'texas chainsaw massacre', "child's play",
                         'evil dead', 'hellraiser', 'candyman']:
                if movie in query_lower:
                    movie_title = movie.title()
                    break
            
            if movie_title:
                # Get movie details first so we can pass to context fusion
                movie_details = get_movie_details_from_apis(movie_title)
                if movie_details and movie_details.get("title"):
                    # ===== RLOM: Store movie in reference buffer =====
                    user_ref_buffer.add_entity("movie", movie_details.get("title"))
                print(f"⏱️ After movie details: {time.time() - start_time:.2f}s")
                
                print(f"⏱️ Before Context Fusion: {time.time() - start_time:.2f}s")
                answer = generate_oracle_response_with_fusion(user_input, omdb_data=movie_details, conversation_history=conversation_history, rlom_context=rlom_context)
                print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
                
                if movie_details:
                    recommendations = get_movie_recommendations(movie_title)
            else:
                answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
            
            # Add conversational wrapper ONLY if client is available
            if use_conversation and client:
                try:
                    conversation_data = oracle_conversation_node(
                        user_input, session_id, conversation_history, query_type, session_data, user_profile
                    )
                    # Enhance factual response with conversational follow-up
                    if conversation_data and conversation_data.get("follow_up_question"):
                        answer += f"\n\n{conversation_data['follow_up_question']}"
                except Exception as e:
                    print(f"⚠️ Conversation layer error (non-fatal): {e}")
                    # Don't fail if conversation layer errors - we already have RAG answer
        
        elif query_type == 'specific_movie':
            # Use extracted movie title if available, otherwise try to extract or use user input
            search_title = extracted_movie or movie_title or user_input
            
            # Use pre-computed intent from early routing
            # When intent is 'api', we should actually USE the API to search for movie details
            if intent == 'api':
                print(f'🔍 Intent is API - searching for movie details: {search_title}')
                movie_details = get_movie_details_from_apis(search_title)
                print(f"⏱️ After API search: {time.time() - start_time:.2f}s")
                
                if movie_details and movie_details.get("title"):
                    # ===== RLOM: Store movie in reference buffer for follow-up questions =====
                    user_ref_buffer.add_entity("movie", movie_details.get("title"))
                    # Also extract and store characters/killers if mentioned
                    if movie_details.get("director"):
                        user_ref_buffer.add_entity("director", movie_details.get("director"))
                    
                    # Get recommendations for this specific movie
                    recommendations = get_movie_recommendations(movie_details.get("title"))
                    print(f"⏱️ After get_recommendations: {time.time() - start_time:.2f}s")
            else:
                # For memory-based queries, still try to get movie details if it looks like a movie title
                movie_details = None
                if search_title or user_ref_buffer.last_movie:
                    movie_title_to_search = search_title if search_title else user_ref_buffer.last_movie
                    movie_details = get_movie_details_from_apis(movie_title_to_search)
                    if movie_details and movie_details.get("title"):
                        user_ref_buffer.add_entity("movie", movie_details.get("title"))
            
            # Get movie details if we haven't gotten them yet
            if movie_details is None:
                # Try to get movie details for context fusion
                movie_details = get_movie_details_from_apis(search_title)
                if movie_details and movie_details.get("title"):
                    user_ref_buffer.add_entity("movie", movie_details.get("title"))
            
            print(f"⏱️ Before Context Fusion: {time.time() - start_time:.2f}s")
            answer = generate_oracle_response_with_fusion(user_input, omdb_data=movie_details, conversation_history=conversation_history, rlom_context=rlom_context)
            print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
            
            # Add conversational wrapper ONLY if we have movie details and client is available
            # Don't use conversation layer as primary response for specific movie queries
            if use_conversation and movie_details and client:
                try:
                    conversation_data = oracle_conversation_node(
                        user_input, session_id, conversation_history, query_type, session_data, user_profile
                    )
                    if conversation_data and conversation_data.get("follow_up_question"):
                        answer += f"\n\n{conversation_data['follow_up_question']}"
                except Exception as e:
                    print(f"⚠️ Conversation layer error (non-fatal): {e}")
                    # Don't fail if conversation layer errors - we already have movie info
        else:
            # For general queries, FIRST try to get movie details if it looks like a movie title
            # This ensures we always search for movies even if query type is "general"
            # Check if we can extract a movie title from the query (even if it's a question)
            search_title = extracted_movie or (user_input if looks_like_movie_title(user_input) else None)
            
            if search_title or looks_like_movie_title(user_input):
                print(f"🎬 General query but contains movie reference - attempting movie search first: {search_title or user_input}")
                # Use pre-computed intent from early routing
                if intent == 'api':
                    print(f'🔍 Intent is API - searching for movie details: {search_title or user_input}')
                    movie_details = get_movie_details_from_apis(search_title or user_input)
                    print(f"⏱️ After API search: {time.time() - start_time:.2f}s")
                else:
                    # Still try to search even if intent is memory-based
                    movie_details = get_movie_details_from_apis(search_title or user_input)
                
                if movie_details and movie_details.get("title"):
                    # ===== RLOM: Store movie in reference buffer =====
                    user_ref_buffer.add_entity("movie", movie_details.get("title"))
                    
                    # Found a movie! Get recommendations and generate appropriate response
                    recommendations = get_movie_recommendations(movie_details.get("title"))
                    print(f"⏱️ After get_recommendations: {time.time() - start_time:.2f}s")
                    
                    # Generate response with context fusion about the movie
                    print(f"⏱️ Before Context Fusion (movie found): {time.time() - start_time:.2f}s")
                    answer = generate_oracle_response_with_fusion(user_input, omdb_data=movie_details, conversation_history=conversation_history, rlom_context=rlom_context)
                    print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
                    
                    # Optionally add conversational follow-up if available
                    if use_conversation and client:
                        try:
                            conversation_data = oracle_conversation_node(
                                user_input, session_id, conversation_history, 'specific_movie', session_data, user_profile
                            )
                            if conversation_data and conversation_data.get("follow_up_question"):
                                answer += f"\n\n{conversation_data['follow_up_question']}"
                        except Exception as e:
                            print(f"⚠️ Conversation layer error (non-fatal): {e}")
                else:
                    # No movie found, continue with general query handling
                    print(f"❌ No movie found for query, continuing as general query")
                    movie_details = None
            
            # If no movie was found or query doesn't look like a movie, handle as general query
            if not movie_details or not movie_details.get("title"):
                # General query - try conversational layer first, but fallback to RAG if it fails
                if use_conversation and client:
                    try:
                        print(f"⏱️ Before conversation layer: {time.time() - start_time:.2f}s")
                        conversation_data = oracle_conversation_node(
                            user_input, session_id, conversation_history, query_type, session_data, user_profile
                        )
                        print(f"⏱️ After conversation layer: {time.time() - start_time:.2f}s")
                        
                        if conversation_data and conversation_data.get("response"):
                            answer = conversation_data.get("response", "")
                            # Still try context fusion for context if needed
                            if len(answer) < 100:  # If response is too short, add context fusion
                                rag_answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
                                answer = f"{answer}\n\n{rag_answer}"
                        else:
                            # Fallback to context fusion if conversation layer returns empty
                            print(f"⏱️ Before Context Fusion (fallback): {time.time() - start_time:.2f}s")
                            answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
                            print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
                    except Exception as e:
                        print(f"⚠️ Conversation layer error, falling back to context fusion: {e}")
                        # Fallback to context fusion if conversation layer fails
                        print(f"⏱️ Before Context Fusion (error fallback): {time.time() - start_time:.2f}s")
                        answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
                        print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
                else:
                    print(f"⏱️ Before Context Fusion: {time.time() - start_time:.2f}s")
                    answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
                    print(f"⏱️ After Context Fusion: {time.time() - start_time:.2f}s")
                
                # Get recommendations for categories
                if query_type in ['bloodiest', 'zombies', 'vampires', 'slashers']:
                    category_movies = HORROR_KNOWLEDGE.get(query_type, [])
                    if category_movies and isinstance(category_movies[0], dict):
                        sample_movie = category_movies[0]
                        movie_details = get_movie_details_from_apis(sample_movie.get('title', ''))
                        if movie_details:
                            recommendations = get_movie_recommendations(sample_movie.get('title', ''))
                    elif category_movies:
                        sample_title = category_movies[0].split('(')[0].strip()
                        movie_details = get_movie_details_from_apis(sample_title)
                        if movie_details:
                            recommendations = get_movie_recommendations(sample_title)
        
        # ===== RLOM INTEGRATION: Extract entities from answer and store =====
        # Safety check: ensure answer is set
        if answer is None:
            print("⚠️ Answer was not set, using fallback")
            answer = generate_oracle_response_with_fusion(user_input, conversation_history=conversation_history, rlom_context=rlom_context)
        
        response_entities = extract_entities_from_text(answer)
        for entity in response_entities:
            user_ref_buffer.add_entity(entity["kind"], entity["value"])
        
        # Determine subject hint for RLOM (the movie being discussed)
        subject_hint = None
        if movie_details and movie_details.get("title"):
            subject_hint = movie_details.get("title")
        elif user_ref_buffer.last_movie:
            subject_hint = user_ref_buffer.last_movie
        
        # ===== RLOM: Memory - Store the conversation turn =====
        if rlom_bridge:
            try:
                rlom_bridge.remember_turn(session_id, resolved, answer, subject_hint=subject_hint)
                print(f"💾 RLOM stored conversation turn")
            except Exception as e:
                print(f"⚠️ RLOM remember_turn error: {e}")
        
        # Update state with entities from the conversation
        state.update_entities(user_input, answer)
        state.add_turn(user_input, answer)
        
        # If we found a movie, make sure it's in state and RLOM buffer
        if movie_details and movie_details.get("title"):
            user_ref_buffer.add_entity("movie", movie_details.get("title"))
            state.last_movie = movie_details.get("title")
        
        # Add Oracle's response to session history
        add_message_to_session(session_id, "assistant", answer)
        
        # Save messages to FAISS memory for retrieval (backward compatibility)
        mem.add_message("user", user_input)
        mem.add_message("assistant", answer)
        store.save(session_id, mem)
        print(f"💾 Saved messages to FAISS memory for session {session_id[:8]}")
        
        # Update last movie discussed if applicable
        if movie_details:
            movie_title = movie_details.get("title")
            if movie_title:
                session_data["last_movie_discussed"] = movie_title
        
        # Save session periodically
        if session_data.get("conversation_turn", 0) % 5 == 0:
            sync_sessions()
        
        # ===== RLOM: Save user context to disk after each message =====
        context_data = {
            "entities": [{"kind": e["kind"], "value": e["value"]} for e in user_ref_buffer.entities],
            "last_movie": user_ref_buffer.last_movie,
            "last_character": user_ref_buffer.last_character,
            "last_killer": user_ref_buffer.last_killer,
            "last_time_ref": user_ref_buffer.last_time_ref
        }
        TemporaryMemory.save_context(session_id, context_data)
        
        print(f"⏱️ TOTAL TIME: {time.time() - start_time:.2f}s")
        
        # Build response
        response = {
            "response": answer,
            "movie_details": movie_details,
            "recommendations": recommendations,
            "query_type": query_type
        }
        
        # Add conversation metadata
        if conversation_data:
            response["personality_tone"] = conversation_data.get("personality_tone")
            response["conversation_turn"] = session_data.get("conversation_turn", 0)
            if conversation_data.get("personality_transition"):
                response["personality_transition"] = conversation_data["personality_transition"]
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in ask-oracle: {e}")
        import traceback
        traceback.print_exc()
        print(f"⏱️ TOTAL TIME (with error): {time.time() - start_time:.2f}s")
        return jsonify({"error": str(e)}), 500

@app.route("/submit-rating", methods=["POST"])
def submit_rating():
    """Submit a rating for a movie"""
    try:
        data = request.json
        movie_title = data.get("movie_title")
        rating = data.get("rating")
        
        if not movie_title or rating is None:
            return jsonify({"error": "Movie title and rating required"}), 400
        
        if not 1 <= rating <= 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        
        movie_ratings[movie_title.lower()].append(rating)
        
        ratings_list = movie_ratings[movie_title.lower()]
        avg_rating = sum(ratings_list) / len(ratings_list)
        
        return jsonify({
            "average_rating": round(avg_rating, 1),
            "total_ratings": len(ratings_list),
            "message": "Rating submitted successfully!"
        })
        
    except Exception as e:
        print(f"Error submitting rating: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/submit-review", methods=["POST"])
def submit_review():
    """Submit a review for a movie"""
    try:
        data = request.json
        movie_title = data.get("movie_title")
        review_text = data.get("review")
        
        if not movie_title or not review_text:
            return jsonify({"error": "Movie title and review text required"}), 400
        
        if len(review_text) > 500:
            return jsonify({"error": "Review must be 500 characters or less"}), 400
        
        review = {
            "text": review_text,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": "Anonymous"
        }
        
        movie_reviews[movie_title.lower()].append(review)
        if len(movie_reviews[movie_title.lower()]) > 10:
            movie_reviews[movie_title.lower()].pop(0)
        
        return jsonify({
            "message": "Review submitted successfully!",
            "total_reviews": len(movie_reviews[movie_title.lower()])
        })
        
    except Exception as e:
        print(f"Error submitting review: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-movie-stats", methods=["GET"])
def get_movie_stats():
    """Get community stats for a movie"""
    try:
        movie_title = request.args.get("movie_title", "").lower()
        
        if not movie_title:
            return jsonify({"error": "Movie title required"}), 400
        
        ratings_list = movie_ratings.get(movie_title, [])
        avg_rating = sum(ratings_list) / len(ratings_list) if ratings_list else 0
        
        reviews_list = movie_reviews.get(movie_title, [])
        
        stats = MOVIE_HORROR_STATS.get(movie_title, {
            "gore": random.randint(20, 95),
            "fear": round(random.uniform(5.0, 10.0), 1),
            "kills": random.randint(1, 25)
        })
        
        return jsonify({
            "rating": {
                "average": round(avg_rating, 1),
                "count": len(ratings_list)
            },
            "reviews": reviews_list[-5:],
            "stats": stats
        })
        
    except Exception as e:
        print(f"Error getting movie stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/theater-releases", methods=["GET"])
def theater_releases():
    """Get current horror movies in theaters with posters"""
    if not TMDB_API_KEY:
        return jsonify({"releases": []})
    
    try:
        today = datetime.datetime.now()
        four_weeks_ago = today - datetime.timedelta(days=28)
        
        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": "27",
            "primary_release_date.gte": four_weeks_ago.strftime("%Y-%m-%d"),
            "primary_release_date.lte": today.strftime("%Y-%m-%d"),
            "sort_by": "popularity.desc",
            "page": 1,
            "region": "US"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        releases = []
        for movie in data.get("results", [])[:3]:
            releases.append({
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "poster_path": movie.get("poster_path"),
                "vote_average": movie.get("vote_average", 0),
                "overview": movie.get("overview", "")[:150] + "..."
            })
        
        return jsonify({"releases": releases})
        
    except Exception as e:
        print(f"Error getting theater releases: {e}")
        return jsonify({"releases": []})

@app.route("/recent-releases", methods=["GET"])
def recent_releases():
    """Get recent horror movie releases with posters"""
    if not TMDB_API_KEY:
        return jsonify({"releases": []})
    
    try:
        today = datetime.datetime.now()
        three_months_ago = today - datetime.timedelta(days=90)
        
        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": "27",
            "primary_release_date.gte": three_months_ago.strftime("%Y-%m-%d"),
            "primary_release_date.lte": today.strftime("%Y-%m-%d"),
            "sort_by": "primary_release_date.desc",
            "page": 1
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        releases = []
        for movie in data.get("results", [])[:10]:
            releases.append({
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "poster_path": movie.get("poster_path"),
                "overview": movie.get("overview", "")[:150] + "..."
            })
        
        return jsonify({"releases": releases})
        
    except Exception as e:
        print(f"Error getting recent releases: {e}")
        return jsonify({"releases": []})

@app.route("/random-genre/<genre>", methods=["GET"])
def random_genre(genre):
    """Get a random movie from a specific horror genre"""
    try:
        genre_movies = {
            "slashers": [
                "Halloween", "Friday the 13th", "A Nightmare on Elm Street", "Scream",
                "Child's Play", "Texas Chainsaw Massacre", "Candyman", "I Know What You Did Last Summer",
                "Black Christmas", "My Bloody Valentine", "Sleepaway Camp", "The Burning"
            ],
            "zombies": [
                "Dawn of the Dead", "28 Days Later", "Train to Busan", "Shaun of the Dead",
                "Night of the Living Dead", "World War Z", "Zombieland", "Return of the Living Dead",
                "Day of the Dead", "28 Weeks Later", "Dead Snow", "Rec"
            ],
            "vampires": [
                "Let the Right One In", "Interview with the Vampire", "30 Days of Night",
                "Near Dark", "The Lost Boys", "Blade", "From Dusk Till Dawn",
                "What We Do in the Shadows", "Nosferatu", "Bram Stoker's Dracula", "Fright Night"
            ],
            "gore-fests": [
                "Evil Dead", "Dead Alive", "Terrifier", "Saw", "Hostel", "The Green Inferno",
                "Tokyo Gore Police", "Machine Girl", "Braindead", "Bad Taste", "Dead Snow"
            ],
            "supernatural": [
                "The Conjuring", "Insidious", "Sinister", "The Babadook", "Poltergeist",
                "The Exorcist", "The Ring", "The Grudge", "Paranormal Activity"
            ],
            "demons": [
                "The Exorcist", "Hellraiser", "Evil Dead", "The Conjuring", "Insidious",
                "Sinister", "Drag Me to Hell", "The Possession", "Demons", "Night of the Demons"
            ],
            "psycho-killers": [
                "Psycho", "The Silence of the Lambs", "American Psycho", "Henry: Portrait of a Serial Killer",
                "Maniac", "The Strangers", "You're Next", "The Purge", "Funny Games"
            ],
            "alien-horror": [
                "Alien", "The Thing", "Invasion of the Body Snatchers", "They Live",
                "Event Horizon", "Life", "The Faculty", "Attack the Block", "Color Out of Space"
            ],
            "creature-features": [
                "The Descent", "Tremors", "Jeepers Creepers", "Dog Soldiers", "The Ritual",
                "Crawl", "Alligator", "Jaws", "The Host", "Cloverfield", "A Quiet Place"
            ],
            "haunted-houses": [
                "The Haunting", "House on Haunted Hill", "The Amityville Horror", "Poltergeist",
                "The Changeling", "Hell House LLC", "Sinister", "Insidious", "The Conjuring"
            ],
            "psychological": [
                "The Babadook", "Black Swan", "Shutter Island", "The Others", "Rosemary's Baby",
                "Don't Look Now", "The Machinist", "Jacob's Ladder", "Mulholland Drive"
            ],
            "cult-horror": [
                "The Wicker Man", "Rosemary's Baby", "Midsommar", "The Witch", "Apostle",
                "Kill List", "Red State", "Martha Marcy May Marlene", "The Invitation"
            ]
        }
        
        movies = genre_movies.get(genre.lower(), [])
        
        if not movies:
            return jsonify({"error": f"Genre '{genre}' not found"}), 404
        
        import random
        selected_movie = random.choice(movies)
        
        movie_details = get_movie_details_from_apis(selected_movie)
        recommendations = []
        
        if movie_details and movie_details.get("title"):
            recommendations = get_movie_recommendations(movie_details["title"])
        
        genre_responses = {
            "slashers": f"SLASHER PICK: {selected_movie}! Classic masked killer mayhem with plenty of creative kills.",
            "zombies": f"ZOMBIE PICK: {selected_movie}! Brain-munching undead action at its finest.",
            "vampires": f"VAMPIRE PICK: {selected_movie}! Bloodsucking terror from the children of the night.",
            "gore-fests": f"GORE FEST: {selected_movie}! Prepare for gallons of blood and extreme violence.",
            "supernatural": f"SUPERNATURAL: {selected_movie}! Ghostly encounters and paranormal terror.",
            "demons": f"DEMONIC: {selected_movie}! Hell's minions bring pure evil to Earth.",
            "psycho-killers": f"PSYCHO KILLER: {selected_movie}! Human monsters are the scariest of all.",
            "alien-horror": f"ALIEN HORROR: {selected_movie}! Terror from beyond the stars.",
            "creature-features": f"CREATURE FEATURE: {selected_movie}! Monsters, beasts, and things that go bump.",
            "haunted-houses": f"HAUNTED HOUSE: {selected_movie}! Spooky dwellings with dark secrets.",
            "psychological": f"PSYCHOLOGICAL: {selected_movie}! Mind-bending terror that gets under your skin.",
            "cult-horror": f"CULT HORROR: {selected_movie}! Religious fanatics and occult nightmares."
        }
        
        response_text = genre_responses.get(genre.lower(), f"Horror pick: {selected_movie}!")
        
        return jsonify({
            "response": response_text,
            "movie_details": movie_details,
            "recommendations": recommendations,
            "query_type": "genre_selection",
            "genre": genre
        })
        
    except Exception as e:
        print(f"Error in random-genre: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-trailer", methods=["GET"])
def get_trailer():
    """Get YouTube trailer URL for a movie"""
    try:
        movie_title = request.args.get("title", "").strip()
        
        if not movie_title or not TMDB_API_KEY:
            return jsonify({"error": "Missing title or TMDB API key"}), 400
        
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={quote(movie_title)}"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        if not search_data.get("results"):
            return jsonify({"error": "Movie not found"}), 404
        
        movie_id = search_data["results"][0]["id"]
        
        videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
        videos_response = requests.get(videos_url)
        videos_data = videos_response.json()
        
        for video in videos_data.get("results", []):
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                youtube_url = f"https://www.youtube.com/watch?v={video['key']}"
                return jsonify({"trailer_url": youtube_url})
        
        return jsonify({"error": "No trailer found"}), 404
        
    except Exception as e:
        print(f"Trailer error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/quiz")
def quiz():
    movie = request.args.get("movie", "unknown")
    prompt = f"""
    Write 10 multiple-choice trivia questions about the horror movie '{movie}'.
    Format as JSON:
    [
      {{ "question": "Question text", "options": ["A","B","C","D"], "answer": "A" }},
      ...
    ]
    """
    
    if client:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            import json
            data = json.loads(resp.choices[0].message.content)
        except Exception:
            data = {"error": "format error"}
    else:
        data = {"error": "OpenAI API not configured"}
    
    return jsonify({"movie": movie, "questions": data})

# ===== OLD QUIZ ROUTES REMOVED - NOW USING ORACLE ENGINE =====
# The old chamber-based quiz system has been replaced by the Oracle Engine
# See Oracle Engine routes below for the new implementation

# ===== HORROR ORACLE LANGGRAPH API =====

# ----- QUIZ PREFETCH SYSTEM -----

def generate_quiz_background():
    """Generate next quiz in background and store in cache."""
    global quiz_cache
    try:
        print("🧩 Generating next quiz in background...")
        new_quiz = start_first_quiz(user_id="auto_prefetch")
        with quiz_lock:
            quiz_cache = new_quiz
        print("✅ Next quiz cached and ready.")
    except Exception as e:
        print(f"⚠️ Prefetch error: {e}")

@app.route("/api/start_quiz", methods=["GET", "POST"])
def api_start_quiz():
    """Starts a horror quiz for a given user and returns JSON.
    
    Supports both GET (user_id as query param) and POST (user_id in JSON body).
    Uses prefetch cache for instant response, then generates next quiz in background.
    
    Optional parameters:
    - difficulty: Override difficulty (beginner, intermediate, advanced, expert)
    - theme: Override theme (general_horror, slasher, psychological, etc.)
    """
    global quiz_cache
    start_time = time.time()
    
    # Handle both GET and POST methods
    if request.method == 'GET':
        user_id = request.args.get('user_id', 'default_user')
        print("🎬 /api/start_quiz called for user:", user_id)
        override_difficulty = None
        override_theme = None
    else:  # POST
        data = request.get_json(silent=True) or {}
        user_id = data.get("userId") or data.get("user_id", "guest")  # Support both formats
        override_difficulty = data.get("difficulty")
        override_theme = data.get("theme")
        print(f"\n{'='*60}")
        print(f"[/api/start_quiz] NEW REQUEST (POST) - User: {user_id}")
        print(f"⏱️  Request received at: {time.time() - start_time:.3f}s")
        if override_difficulty:
            print(f"[/api/start_quiz] Override Difficulty: {override_difficulty}")
        if override_theme:
            print(f"[/api/start_quiz] Override Theme: {override_theme}")
    
    try:
        response_quiz = None
        
        # Check if we have a cached quiz available
        with quiz_lock:
            if quiz_cache:
                response_quiz = quiz_cache
                quiz_cache = None  # Clear cache for next cycle
                print("✅ Using CACHED quiz (instant response)")
            else:
                print("⚠️ No cache available; generating new quiz live...")
        
        # If no cache, generate fresh
        if not response_quiz:
            before_oracle = time.time()
            print(f"⏱️  Before start_first_quiz: {before_oracle - start_time:.3f}s")
            response_quiz = start_first_quiz(user_id)
            after_oracle = time.time()
            print(f"⏱️  After start_first_quiz: {after_oracle - start_time:.3f}s")
            print(f"⏱️  Oracle Engine took: {after_oracle - before_oracle:.3f}s")
            print("✅ LangChain quiz generated:", list(response_quiz.keys()) if isinstance(response_quiz, dict) else "Result received")
        
        # If override parameters provided, regenerate with those parameters
        if override_difficulty or override_theme:
            from oracle_engine.builder_node import BuilderNode
            from oracle_engine.profile_node import ProfileNode
            from oracle_engine.lore_whisperer_node import LoreWhispererNode
            
            builder = BuilderNode()
            profile_node = ProfileNode()
            lore_node = LoreWhispererNode()
            
            # Get user profile
            user_profile = profile_node.get_profile(user_id)
            if not user_profile.get("name"):
                user_profile = response_quiz.get("player_profile", {})
            
            # Override difficulty and theme
            if override_difficulty:
                user_profile["difficulty_level"] = override_difficulty
            if override_theme:
                user_profile["favorite_theme"] = override_theme
            
            # Generate new quiz with overrides
            print(f"[OVERRIDE] Regenerating with difficulty={override_difficulty or 'default'}, theme={override_theme or 'default'}")
            quiz_data = builder.generate_quiz(
                user_profile=user_profile,
                difficulty=override_difficulty or user_profile.get("difficulty_level", "intermediate"),
                theme=override_theme or user_profile.get("favorite_theme", "general_horror")
            )
            
            # Generate new lore
            lore_context = {
                "user_profile": user_profile,
                "theme": quiz_data.get("theme", "horror"),
                "emotion": "indifferent",
                "performance": "beginning"
            }
            lore_output = lore_node.generate_lore(lore_context)
            
            # Update quiz with new data
            response_quiz["room"] = quiz_data.get("room")
            response_quiz["intro"] = quiz_data.get("intro")
            response_quiz["questions"] = quiz_data.get("questions")
            response_quiz["theme"] = quiz_data.get("theme")
            response_quiz["difficulty"] = quiz_data.get("difficulty")
            response_quiz["tone"] = quiz_data.get("tone")
            response_quiz["lore"] = lore_output
            
            print(f"[OK] Quiz regenerated with overrides")
        
        # Start background generation for next quiz
        threading.Thread(target=generate_quiz_background, daemon=True).start()
        print("🔄 Background prefetch started for next quiz")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  TOTAL /api/start_quiz TIME: {total_time:.3f}s")
        print(f"{'='*60}\n")
        return jsonify(response_quiz)
    except Exception as e:
        total_time = time.time() - start_time
        print(f"Quiz generation failed: {e}")
        print(f"⏱️  TOTAL TIME (with error): {total_time:.3f}s")
        import traceback
        traceback.print_exc()
        
        # Start background generation even on error
        threading.Thread(target=generate_quiz_background, daemon=True).start()
        
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500


@app.route("/api/submit_answers", methods=["POST"])
def api_submit_answers():
    """Evaluates submitted answers and returns the score, reaction, and next-step data."""
    start_time = time.time()
    data = request.get_json(force=True)  # Use force=True to handle empty bodies
    user_id = data.get("userId") or data.get("user_id", "guest")  # Support both formats
    quiz = data.get("quiz", {})
    answers = data.get("answers", {})
    
    print("📩 /api/submit_answers called for user:", user_id)
    print(f"\n⏱️  [/api/submit_answers] Starting evaluation...")
    try:
        before_eval = time.time()
        result = evaluate_and_progress(user_id, quiz, answers)
        after_eval = time.time()
        print(f"⏱️  evaluate_and_progress took: {after_eval - before_eval:.3f}s")
        print(f"⏱️  TOTAL /api/submit_answers TIME: {after_eval - start_time:.3f}s\n")
        return jsonify(result)
    except Exception as e:
        print("❌ LangChain submit_answers error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_cached_quiz", methods=["GET"])
def api_get_cached_quiz():
    """Return cached quiz instantly, if available.
    
    This endpoint returns the prefetched quiz immediately without any generation delay.
    If no cache is available, it falls back to generating a new quiz.
    """
    global quiz_cache
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"[/api/get_cached_quiz] REQUEST")
    print(f"⏱️  Request received at: {time.time() - start_time:.3f}s")
    
    try:
        with quiz_lock:
            if quiz_cache:
                cached = quiz_cache
                quiz_cache = None  # Clear cache
                print("✅ Returning CACHED quiz (instant)")
                
                # Start background generation for next quiz
                threading.Thread(target=generate_quiz_background, daemon=True).start()
                print("🔄 Background prefetch started for next quiz")
                
                total_time = time.time() - start_time
                print(f"⏱️  TOTAL /api/get_cached_quiz TIME: {total_time:.3f}s")
                print(f"{'='*60}\n")
                return jsonify(cached)
            else:
                print("⚠️ Cache empty; fallback to live generation.")
        
        # No cache available, generate new quiz
        before_oracle = time.time()
        new_quiz = start_first_quiz(user_id="fallback_cache")
        after_oracle = time.time()
        print(f"⏱️  Live generation took: {after_oracle - before_oracle:.3f}s")
        
        # Start background generation for next quiz
        threading.Thread(target=generate_quiz_background, daemon=True).start()
        print("🔄 Background prefetch started for next quiz")
        
        total_time = time.time() - start_time
        print(f"⏱️  TOTAL /api/get_cached_quiz TIME: {total_time:.3f}s")
        print(f"{'='*60}\n")
        return jsonify(new_quiz)
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"Error in get_cached_quiz: {e}")
        print(f"⏱️  TOTAL TIME (with error): {total_time:.3f}s")
        import traceback
        traceback.print_exc()
        
        # Start background generation even on error
        threading.Thread(target=generate_quiz_background, daemon=True).start()
        
        return jsonify({"error": f"Quiz retrieval failed: {str(e)}"}), 500

# END OF HORROR ORACLE LANGGRAPH API

# ===== AI-ADAPTIVE QUIZ SYSTEM =====

@app.route("/generate-adaptive-quiz", methods=["POST"])
def generate_adaptive_quiz():
    """Generate an AI-adaptive 5-question quiz based on user's horror DNA"""
    try:
        data = request.json
        google_id = data.get('googleId')
        quiz_number = data.get('quizNumber', 1)
        
        # Load user's horror DNA
        users = load_user_data()
        horror_dna = {}
        
        if google_id and google_id in users:
            horror_dna = users[google_id].get('horror_dna', {
                'favorite_themes': [],
                'fear_tolerance': 50,
                'preferred_eras': [],
                'personality_traits': [],
                'quiz_history': []
            })
        
        # Build adaptive prompt based on horror DNA
        prompt = build_adaptive_quiz_prompt(horror_dna, quiz_number)
        
        if not client:
            # Fallback to curated adaptive questions
            questions = get_fallback_adaptive_questions(horror_dna, quiz_number)
            return jsonify({
                "questions": questions,
                "quiz_number": quiz_number,
                "theme": "General Horror",
                "difficulty": "Medium"
            })
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.9
            )
            
            questions_text = resp.choices[0].message.content.strip()
            # Try to parse JSON
            if questions_text.startswith('```'):
                questions_text = questions_text.split('```')[1]
                if questions_text.startswith('json'):
                    questions_text = questions_text[4:]
            
            questions_data = json.loads(questions_text)
            
            # Ensure correct format
            questions = []
            for q in questions_data:
                questions.append({
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct": q.get("correct", 0),
                    "is_profile": q.get("is_profile", False)
                })
            
            return jsonify({
                "questions": questions[:5],  # Only 5 questions
                "quiz_number": quiz_number,
                "theme": extract_theme(horror_dna, quiz_number),
                "difficulty": calculate_difficulty(horror_dna),
                "ai_message": generate_immersive_message(quiz_number, horror_dna)
            })
            
        except Exception as e:
            print(f"AI Quiz generation error: {e}")
            questions = get_fallback_adaptive_questions(horror_dna, quiz_number)
            return jsonify({
                "questions": questions,
                "quiz_number": quiz_number,
                "theme": "Horror Essentials",
                "difficulty": "Medium"
            })
            
    except Exception as e:
        print(f"Error generating adaptive quiz: {e}")
        return jsonify({"error": str(e)}), 500

def build_adaptive_quiz_prompt(horror_dna, quiz_number):
    """Build a personalized quiz prompt based on horror DNA"""
    
    favorite_themes = horror_dna.get('favorite_themes', [])
    fear_tolerance = horror_dna.get('fear_tolerance', 50)
    quiz_history = horror_dna.get('quiz_history', [])
    
    # Determine theme evolution
    if quiz_number == 1:
        theme_focus = "exploring your general horror preferences"
    elif favorite_themes:
        theme_focus = f"diving deeper into {', '.join(favorite_themes[:2])}"
    else:
        theme_focus = "discovering hidden corners of horror cinema"
    
    # Determine difficulty
    if fear_tolerance > 70:
        difficulty = "challenging with obscure references"
    elif fear_tolerance < 30:
        difficulty = "accessible with mainstream classics"
    else:
        difficulty = "balanced between classics and deep cuts"
    
    prompt = f"""You are creating a HORROR MOVIE quiz. This is quiz #{quiz_number} for this user.

HORROR DNA PROFILE:
- Fear Tolerance: {fear_tolerance}/100
- Favorite Themes: {', '.join(favorite_themes) if favorite_themes else 'Unknown'}
- Quiz History: {len(quiz_history)} completed quizzes
- Current Focus: {theme_focus}

INSTRUCTIONS:
Generate exactly 5 questions about HORROR MOVIES. Questions should be CINEMATIC and CREATIVE (NOT boring trivia):

1. Focus on HORROR MOVIE atmosphere, mood, themes, and creative choices
2. Reference ACTUAL HORROR FILMS (The Exorcist, Halloween, The Shining, The Conjuring, etc.)
3. Be {difficulty}
4. Include 1 profile question (marked with "is_profile": true) to learn user preferences about HORROR
5. ALL questions must be about HORROR MOVIES, HORROR DIRECTORS, or HORROR CINEMA

EXAMPLE QUESTION TYPES:
- "In The Shining, which scene creates more dread?"
- "Which horror movie atmosphere draws you in more?"
- "Which horror director's vision resonates with you?"
- "What kind of horror villain terrifies you most?"
- "Which horror movie ending would haunt you longer?"

OUTPUT FORMAT (strict JSON):
[
  {{
    "question": "Question about a HORROR MOVIE scene, director, or atmosphere",
    "options": ["Option A referencing horror", "Option B referencing horror", "Option C referencing horror", "Option D referencing horror"],
    "correct": 0,
    "is_profile": false
  }},
  ...
]

CRITICAL RULES:
- Make sure exactly ONE question has "is_profile": true
- ALL questions MUST be about HORROR MOVIES
- Reference specific horror films, directors, or horror cinema techniques
- Keep questions focused on mood, atmosphere, and creative choices in HORROR"""

    return prompt

def extract_theme(horror_dna, quiz_number):
    """Extract the current theme based on horror DNA"""
    favorite_themes = horror_dna.get('favorite_themes', [])
    
    if quiz_number == 1:
        return "Introduction to Darkness"
    elif favorite_themes:
        return f"{favorite_themes[0].title()} Deep Dive"
    else:
        themes = ["Psychological Terror", "Visceral Horror", "Supernatural Dread", "Slasher Nightmares"]
        return random.choice(themes)

def calculate_difficulty(horror_dna):
    """Calculate difficulty based on horror DNA"""
    fear_tolerance = horror_dna.get('fear_tolerance', 50)
    quiz_count = len(horror_dna.get('quiz_history', []))
    
    # Difficulty increases with quiz count and fear tolerance
    base_difficulty = fear_tolerance
    adjusted = base_difficulty + (quiz_count * 5)
    
    if adjusted > 75:
        return "Expert"
    elif adjusted > 50:
        return "Advanced"
    elif adjusted > 25:
        return "Intermediate"
    else:
        return "Beginner"

def generate_immersive_message(quiz_number, horror_dna):
    """Generate creepy immersive messages between rounds"""
    fear_tolerance = horror_dna.get('fear_tolerance', 50)
    
    if quiz_number == 1:
        return "The AI awakens... studying your fear patterns..."
    elif quiz_number == 2:
        return "Your horror DNA is being analyzed... interesting choices..."
    elif quiz_number == 3:
        if fear_tolerance > 60:
            return "I see you enjoy the darkness... let's go deeper..."
        else:
            return "You're cautious... but curiosity pulls you forward..."
    elif quiz_number == 4:
        return "The patterns emerge... your nightmares are taking shape..."
    else:
        return f"Quiz #{quiz_number}: The algorithm knows what scares you now..."

def get_fallback_adaptive_questions(horror_dna, quiz_number):
    """Fallback adaptive questions when OpenAI is unavailable"""
    
    # Profile questions pool
    profile_questions = [
        {
            "question": "Which of these horror scenarios interests you most?",
            "options": [
                "Being trapped with a supernatural entity",
                "Surviving a masked killer's rampage",
                "Uncovering a dark family secret",
                "Escaping a post-apocalyptic nightmare"
            ],
            "correct": 0,
            "is_profile": True
        },
        {
            "question": "What kind of horror atmosphere draws you in?",
            "options": [
                "Foggy, isolated locations with unseen threats",
                "Dark urban settings with human monsters",
                "Bright daylight horror that feels wrong",
                "Gothic mansions with ancient secrets"
            ],
            "correct": 0,
            "is_profile": True
        }
    ]
    
    # Cinematic questions pool
    cinematic_questions = [
        {
            "question": "Which directorial choice creates more dread?",
            "options": [
                "Long, silent takes with mounting tension",
                "Quick cuts with jarring sound design",
                "Steadicam following the victim's perspective",
                "Wide shots showing isolation and scale"
            ],
            "correct": 0,
            "is_profile": False
        },
        {
            "question": "Which ending would haunt you longer?",
            "options": [
                "The monster was inside them all along",
                "They escape but the evil is still out there",
                "Everyone dies and evil wins",
                "Ambiguous - you never know what was real"
            ],
            "correct": 3,
            "is_profile": False
        },
        {
            "question": "What makes a horror villain most terrifying?",
            "options": [
                "No clear motive - pure chaos",
                "Twisted logic that almost makes sense",
                "Former victim seeking revenge",
                "Supernatural force beyond understanding"
            ],
            "correct": 0,
            "is_profile": False
        },
        {
            "question": "Which sound design element creates maximum fear?",
            "options": [
                "Complete silence before the strike",
                "Distorted voices and whispers",
                "Discordant strings and violin shrieks",
                "Realistic sounds - breathing, footsteps"
            ],
            "correct": 0,
            "is_profile": False
        },
        {
            "question": "What type of horror cinematography unsettles you most?",
            "options": [
                "Found footage with shaky realism",
                "Beautiful, symmetrical shots hiding evil",
                "Darkness with minimal lighting",
                "Distorted POV shots from the killer's eyes"
            ],
            "correct": 1,
            "is_profile": False
        }
    ]
    
    # Select 1 profile question and 4 cinematic questions
    selected_profile = random.choice(profile_questions)
    selected_cinematic = random.sample(cinematic_questions, 4)
    
    questions = [selected_profile] + selected_cinematic
    random.shuffle(questions)
    
    return questions

@app.route("/save-quiz-results", methods=["POST"])
def save_quiz_results():
    """Save quiz results and update horror DNA"""
    try:
        data = request.json
        google_id = data.get('googleId')
        quiz_results = data.get('quizResults', {})
        
        if not google_id:
            return jsonify({"error": "Missing googleId"}), 400
        
        users = load_user_data()
        
        # Initialize user if not exists
        if google_id not in users:
            users[google_id] = {
                "myList": [],
                "ratings": {},
                "history": [],
                "genre_searches": {},
                "horror_profile": "New Horror Fan",
                "horror_dna": {
                    "favorite_themes": [],
                    "fear_tolerance": 50,
                    "preferred_eras": [],
                    "personality_traits": [],
                    "quiz_history": []
                }
            }
        
        # Initialize horror_dna if not exists
        if "horror_dna" not in users[google_id]:
            users[google_id]["horror_dna"] = {
                "favorite_themes": [],
                "fear_tolerance": 50,
                "preferred_eras": [],
                "personality_traits": [],
                "quiz_history": []
            }
        
        # Update horror DNA based on quiz results
        horror_dna = users[google_id]["horror_dna"]
        
        # Add quiz to history
        quiz_entry = {
            "quiz_number": len(horror_dna["quiz_history"]) + 1,
            "score": quiz_results.get('score', 0),
            "total": quiz_results.get('total', 5),
            "theme": quiz_results.get('theme', 'General'),
            "answers": quiz_results.get('answers', []),
            "timestamp": datetime.datetime.now().isoformat()
        }
        horror_dna["quiz_history"].append(quiz_entry)
        
        # Update fear tolerance based on score
        score_percent = (quiz_results.get('score', 0) / quiz_results.get('total', 5)) * 100
        current_tolerance = horror_dna.get("fear_tolerance", 50)
        # Gradually increase tolerance with good scores
        new_tolerance = min(100, current_tolerance + (score_percent / 20))
        horror_dna["fear_tolerance"] = new_tolerance
        
        # Extract themes from profile answers
        profile_answers = quiz_results.get('profile_answers', [])
        for answer in profile_answers:
            theme = extract_theme_from_answer(answer)
            if theme and theme not in horror_dna["favorite_themes"]:
                horror_dna["favorite_themes"].append(theme)
        
        # Keep only top 5 themes
        horror_dna["favorite_themes"] = horror_dna["favorite_themes"][:5]
        
        save_user_data(users)
        
        return jsonify({
            "success": True,
            "horror_dna": horror_dna,
            "next_quiz_number": len(horror_dna["quiz_history"]) + 1,
            "immersive_message": generate_immersive_message(len(horror_dna["quiz_history"]) + 1, horror_dna)
        })
        
    except Exception as e:
        print(f"Error saving quiz results: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/rlom", methods=["POST"])
def handle_rlom():
    data = request.get_json()
    user_id = data.get("user_id", "guest")
    message = data.get("message", "")
    result = rlom_process_message(user_id, message)
    return jsonify(result)

def extract_theme_from_answer(answer_text):
    """Extract horror theme from a profile answer"""
    answer_lower = answer_text.lower()
    
    theme_keywords = {
        "supernatural": ["supernatural", "entity", "ghost", "spirit", "paranormal"],
        "slasher": ["killer", "masked", "slasher", "murder"],
        "psychological": ["secret", "mind", "psychological", "mystery"],
        "post-apocalyptic": ["apocalyptic", "survival", "zombie", "outbreak"],
        "gothic": ["gothic", "mansion", "ancient", "castle"],
        "urban": ["urban", "city", "modern"],
        "isolation": ["isolated", "alone", "trap", "fog"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in answer_lower for keyword in keywords):
            return theme
    
    return None

# ===========================
# HORROR ORACLE API ROUTES - Additional logging and verification
# ===========================
# NOTE: /api/start_quiz (GET and POST) and /api/submit_answers (POST) are defined above
# This section confirms they are active with enhanced logging

print("✅ Horror Oracle API active: /api/start_quiz (GET and POST) /api/submit_answers (POST)")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Welcome to my nightmare")
    print("🩸 the Horror Oracle 🩸")
    print("="*50)
    print(f"📊 Server running on http://localhost:5000")
    print(f"🎬 OMDB API: {'CONNECTED' if OMDB_API_KEY else 'MISSING - Limited functionality'}")
    print(f"🎥 TMDB API: {'CONNECTED' if TMDB_API_KEY else 'MISSING - No posters/recommendations'}")
    print(f"🧠 OpenAI: {'CONNECTED' if OPENAI_API_KEY else 'MISSING - Using fallback responses'}")
    print(f"📦 Pinecone: {'CONNECTED' if index else 'DISCONNECTED'}")
    print(f"🗣️  Conversation Layer: ACTIVE")
    print("="*50)
    print("🔄 Starting initial quiz prefetch...")
    print("🔄 Cleaning up old conversation sessions...")
    print("="*50 + "\n")
    
    # Start initial prefetch in background
    threading.Thread(target=generate_quiz_background, daemon=True).start()
    
    # Initialize conversation layer client
    if client:
        try:
            import oracle_conversation.oracle_conversation_node as oracle_node_module
            oracle_node_module.set_client(client)
            print("✅ Conversation layer client initialized")
        except Exception as e:
            print(f"⚠️ Error initializing conversation client: {e}")
    
    # Load conversation sessions from disk
    from oracle_conversation.conversation_memory import load_sessions_from_file
    try:
        loaded_sessions = load_sessions_from_file()
        from oracle_conversation.conversation_memory import conversation_sessions
        conversation_sessions.update(loaded_sessions)
        print(f"✅ Loaded {len(loaded_sessions)} conversation sessions from disk")
    except Exception as e:
        print(f"⚠️ Error loading sessions: {e}")
    
    app.run(host="0.0.0.0", port=5000, debug=True)