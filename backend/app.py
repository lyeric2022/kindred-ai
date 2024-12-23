from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import router
from services import ingest_stories

# Ingest any existing stories on startup
ingest_stories()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the Svelte app's public directory
app.mount("/public", StaticFiles(directory="../svelte-app/public"), name="public")
app.include_router(router)