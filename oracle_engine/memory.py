import faiss
import numpy as np
from openai import OpenAI
import os
import json


class TemporaryMemory:

    def __init__(self):
        self.client = OpenAI()
        self.dimension = 1536  # for text-embedding-3-small
        self.index = faiss.IndexFlatL2(self.dimension)
        self.messages = []
    
    @staticmethod
    def load_context(user_id):
        """Load user context from disk"""
        path = f"profiles/{user_id}_context.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_context(user_id, data):
        """Save user context to disk"""
        os.makedirs("profiles", exist_ok=True)
        with open(f"profiles/{user_id}_context.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def __getstate__(self):
        """Custom pickle serialization for FAISS index."""
        # Save FAISS index to bytes
        index_bytes = faiss.serialize_index(self.index)
        # Return state without client (will be recreated) and with serialized index
        state = self.__dict__.copy()
        del state['client']  # OpenAI client can't be pickled
        state['index'] = index_bytes
        return state

    def __setstate__(self, state):
        """Custom pickle deserialization for FAISS index."""
        # Restore FAISS index from bytes
        if isinstance(state['index'], bytes):
            state['index'] = faiss.deserialize_index(state['index'])
        self.__dict__.update(state)
        # Recreate OpenAI client
        self.client = OpenAI()


    def _embed(self, text):
        emb = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        ).data[0].embedding
        return np.array(emb, dtype="float32")


    def add_message(self, role, text):
        embedding = self._embed(text)
        self.index.add(np.array([embedding]))
        self.messages.append({"role": role, "text": text})


    def retrieve_context(self, query, top_k=5):
        if len(self.messages) == 0:
            return []
        q_vec = self._embed(query).reshape(1, -1)
        scores, indices = self.index.search(q_vec, top_k)
        retrieved = []
        for i in indices[0]:
            if 0 <= i < len(self.messages):
                retrieved.append(self.messages[i]["text"])
        return retrieved


    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.messages = []


    def get_message_count(self):
        """Get the current number of messages stored."""
        return len(self.messages)
    
    def save_message(self, user_id, user_text, bot_text):
        """Save a message to the memory store"""
        # Add both user and bot messages to memory
        if user_text:
            self.add_message("user", user_text)
        if bot_text:
            self.add_message("assistant", bot_text)
    
    def load_messages(self, user_id):
        """Load messages for a user"""
        # Return messages in the format expected by the RLOM bridge
        return self.messages

