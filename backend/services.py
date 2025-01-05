import os
from cerebras_model import load_cerebras_model, generate_answer_cerebras
from pinecone_client import get_relevant_chunks, ingest_stories
from transcription import model as whisper_model

async def transcribe_audio(file):
    file_location = "audio.wav"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    result = whisper_model.transcribe(file_location)
    os.remove(file_location)
    
    # Append new transcription to stories.txt
    data_file_path = os.path.join("data", "stories.txt")
    os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
    with open(data_file_path, "a", encoding="utf-8") as data_file:
        data_file.write(result['text'] + "\n")

    # Re-ingest stories, ensuring new lines become new chunks
    ingest_stories()

    return result['text']

async def handle_transcription(file, request):
    if file:
        transcription = await transcribe_audio(file)
    else:
        data = await request.json()
        transcription = data["text"]
        data_file_path = os.path.join("data", "stories.txt")
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
        with open(data_file_path, "a", encoding="utf-8") as data_file:
            data_file.write(transcription + "\n")
        ingest_stories()
    return transcription

async def handle_question(file, request):
    question = None
    if file:
        file_location = "audio.wav"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        question = whisper_model.transcribe(file_location)['question']
    else:
        data = await request.json()
        question = data["question"]
        
    return await ask_question(question)
   
async def ask_question(question):
    # Retrieve relevant chunks from Pinecone
    relevant_chunks = get_relevant_chunks(question, top_k=3)

    # Load the Cerebras model pipeline
    api_key = os.getenv("CEREBRAS_API_KEY")
    client, model_name = load_cerebras_model(api_key)

    # Generate the answer using Cerebras
    answer = generate_answer_cerebras(client, model_name, question, relevant_chunks)
    return answer