#!/usr/bin/python3

"""
@description: FastAPI backend server that provides API endpoints for audio management
(CRUD, play, stop, pause, volume control) and mood settings. It also serves
audio files from a static directory.
"""

import os
from fastapi import FastAPI, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import lib.soundmood_control as smc
import lib.t2s as t2s
import uvicorn


# ----- CONFIGURATION & APP INITIALIZATION -----

# Point static directory
static_dir = os.path.abspath('lib/audios') 
vAPI = "/v1" # Used as the APIRouter prefix

# *** Static Directory Setup ***
try:
    # Ensure the simplified directory exists before mounting
    os.makedirs(static_dir, exist_ok=True)
    print(f"Ensured directory exists: {static_dir}")
except OSError as e:
    print(f"Error creating directory {static_dir}: {e}")
    raise

# *** FastAPI Initialization ***
app = FastAPI(
    title="Robot audios server",
    description="Robot audios backend using FastAPI."
)

# *** CORS Middlewares ***
# Allows all origins, methods, and headers, matching the original Flask CORS setup.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# *** Static Files ***
# Mounts the static directory to be served under the '/static' path.
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ----- API ROUTER DEFINITION -----
# APIRouter for /v1 prefix
router = APIRouter(prefix=vAPI)


# ----- AUDIO CRUD ENDPOINTS -----

# *** Create/Post Audio ***
@router.post('/audio')
async def post_audio(data: dict = Body(..., description="JSON payload for audio creation/update.")):
    return smc.post_audio(data)

# *** Delete Audio ***
@router.delete('/audio')
async def delete_audio(data: dict = Body(..., description="JSON payload for audio deletion.")):
    return smc.delete_audio(data)

# *** Get/List Audios ***
@router.get('/audio')
def get_audios():
    return smc.get_audios()


# ----- AUDIO PLAYBACK ENDPOINTS -----

# *** Play Audio (by name) ***
@router.get('/play/{audio_file}')
def play(audio_file: str):
    return t2s.playAudio(audio_file)

# *** Stop Audio Playback ***
@router.get('/audio/stop')
def stop():
    return t2s.stop()


# ----- VOLUME CONTROL ENDPOINTS -----

# *** Set Volume (by token/value) ***
@router.get("/audio/volume")
def get_volume():
    return smc.get_volume()

# *** Set Volume (Relative/Add) ***
@router.post("/audio/volume/{value}")
async def set_volume(value):
    return smc.set_volume(value)


# ----- MOOD CONTROL ENDPOINTS -----

# *** Get Available Moods ***
@router.get('/moods')
def get_moods():
    return smc.get_moods()

# *** Set Current Mood ***
@router.post("/moods/{mood}")
def set_mood(mood: str):
    return smc.set_mood(mood)

# *** Get the current mouth state
@router.get("/moods/{state}")
def set_mouth(state: str):
    return smc.set_mouth(state)


# ----- REGISTER ROUTER -----
# Add the router's routes to the main application
app.include_router(router)


# ----- SERVER STARTUP -----

# *** Server Execution Blocks ***
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