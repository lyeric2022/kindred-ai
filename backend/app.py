from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Pinecone client instance
pc = Pinecone(
    api_key="pcsk_37EwVu_M5F15xBKMM9fBHvmWEdMxhLaeNnPup7sDq9cSpPLqbKbBxrFNsjZ5kewxm4pSPq"
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

# Ingest any existing stories on startup
ingest_stories()

app = FastAPI()
model = whisper.load_model("base")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    file_location = "audio.wav"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    result = model.transcribe(file_location)
    os.remove(file_location)
    
    # Append new transcription to stories.txt
    data_file_path = os.path.join("data", "stories.txt")
    os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
    with open(data_file_path, "a", encoding="utf-8") as data_file:
        data_file.write(result['text'] + "\n")

    # Re-ingest stories, ensuring new lines become new chunks
    ingest_stories()

    return JSONResponse({"transcription": result['text']})

@app.get("/")
async def main():
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audio Transcription</title>
    </head>
    <body>
        <h1>Record Audio and Transcribe</h1>
        <button id="recordButton">Record</button>
        <button id="stopButton" disabled>Stop</button>
        <p id="transcription"></p>

        <script>
            let mediaRecorder;
            let audioChunks = [];

            document.getElementById('recordButton').addEventListener('click', async () => {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'audio.wav');

                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    document.getElementById('transcription').innerText = result.transcription;
                };

                document.getElementById('recordButton').disabled = true;
                document.getElementById('stopButton').disabled = false;
            });

            document.getElementById('stopButton').addEventListener('click', () => {
                mediaRecorder.stop();
                document.getElementById('recordButton').disabled = false;
                document.getElementById('stopButton').disabled = true;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)