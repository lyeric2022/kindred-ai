from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from models import QuestionRequest
from services import transcribe_audio, ask_question

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    transcription = await transcribe_audio(file)
    return JSONResponse({"transcription": transcription})

@router.post("/ask")
def ask_question_route(payload: QuestionRequest):
    answer = ask_question(payload.question)
    return {"answer": answer}

@router.get("/")
async def main():
    return FileResponse("../svelte-app/public/index.html")