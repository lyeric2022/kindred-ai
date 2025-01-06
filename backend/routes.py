import os
import logging
from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import JSONResponse
from services import handle_transcription, handle_question, upload_audio, synthesize_audio
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(None), request: Request = None):
    logger.debug(f"Received transcribe request with file: {file} and request: {request}")
    transcription = await handle_transcription(file, request)
    return JSONResponse({"transcription": transcription})

@router.post("/ask")
async def ask_question_route(file: UploadFile = File(None), request: Request = None):
    logger.debug(f"Received ask question request with file: {file} and request: {request}")
    answer = await handle_question(file, request)
    return JSONResponse({"answer": answer})

@router.post("/tts/upload")
async def tts_upload(file: UploadFile = File(...)):
    logger.debug("Received file upload request.")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    temp_path = os.path.join(upload_dir, file.filename)
    
    # Handle duplicate files by renaming
    if os.path.exists(temp_path):
        base, ext = os.path.splitext(temp_path)
        counter = 1
        while os.path.exists(temp_path):
            temp_path = f"{base}_{counter}{ext}"
            counter += 1

    with open(temp_path, "wb") as buffer:
        file_bytes = await file.read()
        logger.debug(f"File size in bytes: {len(file_bytes)}")
        buffer.write(file_bytes)

    logger.debug(f"Saved uploaded file to {temp_path}")
    result = upload_audio(temp_path)
    logger.debug(f"upload_audio result: {result}")

    if not result.get("ref_text"):
        logger.error("Audio upload/transcription failed: 'ref_text' missing.")
        raise HTTPException(status_code=500, detail="Audio upload/transcription failed")
    
    logger.debug("Returning successful JSON response.")
    return JSONResponse(result)

class SynthesisRequest(BaseModel):
    gen_text: str
    ref_text: str | None = None
    ref_audio_path: str | None = None

@router.post("/tts/synthesize")
async def tts_synthesize(request: SynthesisRequest):
    logger.debug(f"Received synthesis request with gen_text: {request.gen_text}, ref_text: {request.ref_text}, ref_audio_path: {request.ref_audio_path}")
    
    result = synthesize_audio(request.gen_text, request.ref_text, request.ref_audio_path)
    logger.debug(f"Synthesis result: {result}")
    
    if not result.get("audio_file"):
        logger.error("Synthesis failed: 'audio_file' missing in result.")
        raise HTTPException(status_code=500, detail="Synthesis failed")
    
    logger.debug("Returning successful JSON response.")
    return JSONResponse(result)