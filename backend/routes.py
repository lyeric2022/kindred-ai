from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
from services import handle_transcription, handle_question

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(None), request: Request = None):
    transcription = await handle_transcription(file, request)
    return JSONResponse({"transcription": transcription})

@router.post("/ask")
async def ask_question_route(file: UploadFile = File(None), request: Request = None):
    answer = await handle_question(file, request)
    return JSONResponse({"answer": answer})