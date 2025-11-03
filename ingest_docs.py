import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Try modern import first, fallback to older versions
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma


# ===== SETUP =====
DATA_DIR = "data/horror_movies"
PERSIST_DIR = "vectorstore"

print("🧠 Starting ingestion...")
os.makedirs(PERSIST_DIR, exist_ok=True)

# ===== LOAD FILES =====
loader = DirectoryLoader(DATA_DIR, glob="*.txt", loader_cls=TextLoader)
documents = loader.load()
print(f"📚 Loaded {len(documents)} documents.")

# ===== SPLIT INTO CHUNKS =====
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.split_documents(documents)
print(f"✂️ Split into {len(docs)} chunks.")

# ===== CREATE EMBEDDINGS =====
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# ===== BUILD VECTOR STORE =====
db = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_DIR)
db.persist()

print(f"✅ Vector database created at: {PERSIST_DIR}")
print("🚀 Ingestion complete.")
