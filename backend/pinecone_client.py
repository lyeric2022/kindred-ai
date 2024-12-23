import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create a Pinecone client instance
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
)
index_name = "memories"

# Create/connect to index
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

# Initialize embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(texts):
    return embedding_model.encode(texts).tolist()

def chunk_text(lines, chunk_size=3):
    """
    Example chunking: group lines of text in sets of 'chunk_size'
    """
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunk = " ".join(lines[i : i + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def upsert_chunks(chunks):
    embeddings = embed_text(chunks)
    upserts = []
    for i, emb in enumerate(embeddings):
        # Each chunk has a unique ID, e.g. "story_0"
        upserts.append((f"story_{i}", emb, {"text": chunks[i]}))
    index.upsert(vectors=upserts)

def ingest_stories():
    """
    Read stories.txt, split into chunks, and store all
    """
    filepath = os.path.join("data", "stories.txt")
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    # Chunk the lines
    story_chunks = chunk_text(lines, chunk_size=2)
    upsert_chunks(story_chunks)

def get_relevant_chunks(question, top_k=3):
    # Embed the question text
    question_embedding = embed_text([question])[0]

    # Query Pinecone for top_k results
    results = index.query(
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Extract and return documents from the results
    documents = [match.metadata.get("text", "") for match in results.matches]
    return documents