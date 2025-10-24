#!/usr/bin/python3

import os
from fastapi import FastAPI, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import lib.soundmood_control as smc
import lib.t2s as t2s
import uvicorn

# --- Configuration ---
# FIXED: Point static directory to the simplified 'lib/audios' path
static_dir = os.path.abspath('lib/audios') 
vAPI = "/v1" # Used as the APIRouter prefix

# --- Static Directory Setup ---
try:
    # Ensure the simplified directory exists before mounting
    os.makedirs(static_dir, exist_ok=True)
    print(f"Ensured directory exists: {static_dir}")
except OSError as e:
    print(f"Error creating directory {static_dir}: {e}")
    raise

# --- FastAPI Initialization ---
app = FastAPI(
    title="Robot audios server",
    description="Robot audios backend using FastAPI."
)

# --- CORS Middlewares ---
# Allows all origins, methods, and headers, matching the original Flask CORS setup.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---
# Mounts the static directory to be served under the '/static' path.
# Now, /static maps directly to the contents of the 'lib/audios' folder.
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- APIRouter for /v1 prefix ---
router = APIRouter(prefix=vAPI)


# CRUD Audios
@router.post('/audio')
async def post_audio(data: dict = Body(..., description="JSON payload for audio creation/update.")):
    return smc.post_audio(data)

@router.delete('/audio')
async def delete_audio(data: dict = Body(..., description="JSON payload for audio deletion.")):
    return smc.delete_audio(data)

@router.get('/audio')
def get_audios():
    return smc.get_audios()


# Playing functions
# Path parameters are defined using standard Python type hints.
@router.get('/play/{texto}')
def play(texto: str):
    t2s.playAudio(texto)
    return {"Status" : True}

@router.get('/stop')
def stop():
    t2s.stop()
    return {"Status" : True}

@router.get("/audio/volume/{token}")
def volume(token: str):
    return smc.volume(token)

@router.post("/audio/volume/add")
async def volume_add(data: dict = Body(...)):
    return smc.volumeAdd(data)

@router.get("/audio/volume")
def get_volume():
    return smc.get_volume()

@router.put("/audio/volume")
async def update_volume(data: dict = Body(...)):
    return smc.update_volume(data)

@router.get("/audio/pausa")
def pausa():
    return t2s.pausa()


# Moods functions
@router.get('/moods')
def get_moods():
    return smc.get_moods()

@router.post("/moods/{mood}")
def set_mood(mood: str):
    return smc.set_mood(mood)


# Add the router's routes to the main application
app.include_router(router)


# --- Server Execution Blocks ---
# For local development with Uvicorn (FastAPI's standard server)
if __name__ == '__main__':
    # The 'reload=True' flag enables hot-reloading for development
    uvicorn.run("app_fastapi:app", host='0.0.0.0', port=9020, reload=True)


# To use Production WSGI Server (Gunicorn)
# The Gunicorn command changes to use the Uvicorn worker class for asynchronous performance:
# $ gunicorn -w 4 -b 0.0.0.0:9020 -k uvicorn.workers.UvicornWorker 'app_fastapi:app'

# -w 4 Sets the number of worker processes (workers).
# -k uvicorn.workers.UvicornWorker Tells Gunicorn to use the high-performance async worker.
# 'app_fastapi:app' references the file name and the FastAPI application object.