# oracle_engine/context_fusion.py

from typing import List, Dict, Any

import re


class ConversationState:
    """
    Very simple in-memory tracker for last movie / last character / last killer.
    This is NOT a database. It's per-process. Good enough for local dev.
    """
    def __init__(self):
        self.chat_history: List[Dict[str, str]] = []
        self.last_movie: str | None = None
        self.last_character: str | None = None
        self.last_killer: str | None = None


    def add_turn(self, user: str, assistant: str):
        self.chat_history.append({"role": "user", "content": user})
        self.chat_history.append({"role": "assistant", "content": assistant})


    def update_entities(self, user_msg: str, llm_answer: str | None = None):
        """
        Try to capture movie names or characters from either the user or the model.
        We're using dumb heuristics because we don't want external deps.
        """
        # If user explicitly says a movie name like "Halloween", "Friday the 13th", "Scream"
        movie_candidates = self._extract_movie_like(user_msg)
        if movie_candidates:
            self.last_movie = movie_candidates[0]


        # character / killer references
        killer_candidates = self._extract_killer_like(user_msg)
        if killer_candidates:
            self.last_killer = killer_candidates[0]
            self.last_character = killer_candidates[0]


        # if LLM answered "The killer is Jason Voorhees." we capture that too
        if llm_answer:
            killer_candidates = self._extract_killer_like(llm_answer)
            if killer_candidates:
                self.last_killer = killer_candidates[0]
                self.last_character = killer_candidates[0]


    def _extract_movie_like(self, text: str) -> List[str]:
        known_movies = [
            "Halloween", "Friday the 13th", "A Nightmare on Elm Street",
            "The Exorcist", "Scream", "The Texas Chain Saw Massacre",
            "Hellraiser", "Child's Play", "The Shining"
        ]
        found = []
        for m in known_movies:
            if m.lower() in text.lower():
                found.append(m)
        return found


    def _extract_killer_like(self, text: str) -> List[str]:
        known_killers = [
            "Jason Voorhees", "Michael Myers", "Freddy Krueger",
            "Chucky", "Pinhead", "Ghostface", "Leatherface", "Pamela Voorhees"
        ]
        found = []
        for k in known_killers:
            if k.lower() in text.lower():
                found.append(k)
        # very simple "he"/"him" resolver: if user said "how old is he" we keep existing
        if not found and ("how old is he" in text.lower() or "was he" in text.lower()):
            # don't overwrite, just keep current
            if self.last_killer:
                return [self.last_killer]
            if self.last_character:
                return [self.last_character]
        return found


state = ConversationState()


def build_fused_context(
    user_msg: str,
    rag_docs: List[Any] | None,
    omdb_data: Dict[str, Any] | None
) -> str:
    """
    Take user message + RAG chunks + OMDB json + state.last_movie/character
    and produce ONE prompt string for the LLM.
    """
    parts: List[str] = []


    parts.append("You are the Horror Oracle. Keep the conversation consistent. If the user refers to 'he', 'she', or 'the killer', use the last known entity from context.")
    parts.append(f"User message: {user_msg}")


    # add current known entities
    if state.last_movie:
        parts.append(f"Current movie in focus: {state.last_movie}")
    if state.last_character:
        parts.append(f"Current character in focus: {state.last_character}")
    if state.last_killer:
        parts.append(f"Current killer in focus: {state.last_killer}")


    # add RAG docs
    if rag_docs:
        rag_texts = "\n\n".join([d.page_content if hasattr(d, "page_content") else str(d) for d in rag_docs])
        parts.append("LOCAL FILE CONTEXT (from FAISS / Chroma):")
        parts.append(rag_texts)


    # add OMDB
    if omdb_data:
        parts.append("OMDB / API CONTEXT:")
        for k, v in omdb_data.items():
            if v:
                parts.append(f"- {k}: {v}")


    # add instruction to stay on subject
    parts.append("IMPORTANT: If the user asks a follow-up like 'how old is he' or 'was he abused', answer about the same killer/character/movie currently in focus. Do NOT ask 'who do you mean' unless there is truly no entity in context.")
    parts.append("If local files don't have an answer, infer from the movie's known universe and answer anyway. Be decisive.")


    return "\n\n".join(parts)


