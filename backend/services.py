import os
import logging
from cerebras_model import load_cerebras_model, generate_answer_cerebras
from pinecone_client import get_relevant_chunks, ingest_stories
from transcription import model as whisper_model
from tts.tts_client import F5TTS

from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize TTS model
tts_model = F5TTS()

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

        question = whisper_model.transcribe(file_location)
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

def upload_audio(file_path: str) -> dict:
    print("HELLO")
    logger.info(f"Uploading audio from {file_path}")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Trim the audio to 15 seconds
    audio = AudioSegment.from_file(file_path)
    trimmed_audio = audio[:15000]  # 15 seconds
    trimmed_file = os.path.join(upload_dir, "uploaded_audio.wav")
    trimmed_audio.export(trimmed_file, format="wav")

    # Transcribe using TTS
    ref_text = tts_model.transcribe(trimmed_file)
    transcribed_text_path = os.path.join(upload_dir, "transcribed_audio.txt")
    with open(transcribed_text_path, "w") as text_file:
        text_file.write(ref_text)

    return {"file_path": trimmed_file, "ref_text": ref_text}

def synthesize_audio(gen_text: str, ref_text: str = None, ref_audio_path: str = None) -> dict:
    logger.info("Synthesis initiated")
    upload_dir = "uploads"
    
    if not ref_audio_path:
        ref_audio_path = os.path.join(upload_dir, "uploaded_audio.wav")
    logger.debug(f"Reference audio path: {ref_audio_path}")

    transcribed_text_path = os.path.join(upload_dir, "transcribed_audio.txt")
    if not ref_text and os.path.exists(transcribed_text_path):
        with open(transcribed_text_path) as f:
            ref_text = f.read()
    logger.debug(f"Reference text: {ref_text}")

    output_audio = "output.mp3"
    logger.debug(f"Generating audio with gen_text: {gen_text}, ref_text: {ref_text}, ref_audio_path: {ref_audio_path}")
    wav, sr, _ = tts_model.infer(
        ref_file=ref_audio_path,
        ref_text=ref_text,
        gen_text=gen_text,
        file_audio=output_audio
    )

    if wav is None:
        logger.error("Synthesis failed: 'wav' is None.")
        return {"audio_file": None}

    logger.info(f"Synthesis successful, output audio file: {output_audio}")
    return {"audio_file": output_audio}