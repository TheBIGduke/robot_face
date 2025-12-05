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

# --- CONFIGURATION & APP INITIALIZATION ---
static_dir = os.path.abspath('lib/audios') 
vAPI = "/v1" # Used as the APIRouter prefix


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
    #allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---
# Mounts the static directory to be served under the '/static' path.
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- APIRouter for /v1 prefix ---
router = APIRouter(prefix=vAPI)


# ----- AUDIO CRUD ENDPOINTS -----
# *** Create/Post Audio ***
@router.post('/audio')
async def post_audio(data: dict = Body(..., description="JSON payload for audio creation/update.")):
    """
    Create an audio file.

    body = { "Mood": "Neutral", "Name": "prueba", "Text": "esta es una prueba"}
    """
    return smc.post_audio(data)

# *** Delete Audio ***
@router.delete('/audio')
async def delete_audio(data: dict = Body(..., description="JSON payload for audio deletion.")):
    """
    Delete an audio file.

    body = {"Name": "Feliz_prueba"}
    """
    return smc.delete_audio(data)

# *** Get/List Audios ***
@router.get('/audio')
def get_audios():
    return smc.get_audios()


# ----- AUDIO PLAYBACK ENDPOINTS -----
# *** Play Audio (by name) ***
@router.get('/play/{audio_file}')
def play(audio_file: str):
    mood = audio_file.split('_')[0]
    if not mood == "":
        smc.set_mood(mood)
    return t2s.playAudio(audio_file)

# *** Stop Audio Playback ***
@router.get('/audio/stop')
def stop():
    return t2s.stop()

# *** Get system volume ***
@router.get("/audio/volume")
def get_volume():
    """
    Get system volume, [0,100]
    """
    return smc.get_volume()

# *** Set system volume ***
@router.post("/audio/volume/{value}")
async def set_volume(value):
    """
    Set system volume, value=[0,100]
    """
    return smc.set_volume(value)


# ----- MOOD CONTROL ENDPOINTS -----
# *** Get Available Moods ***
@router.get('/moods')
def get_moods():
    return smc.get_moods()

# *** Set Mood ***
@router.post("/moods/{mood}")
def set_mood(mood: str):
    return smc.set_mood(mood)

# *** Set the current mouth state (on, off) for all system sounds
@router.get("/moods/{state}")
def set_mouth(state: str):
    """
    Activate/deactivate mouth motion, state=(on,off)
    """
    return smc.set_mouth(state)


# ----- REGISTER ROUTER -----
# Add the router's routes to the main application
app.include_router(router)


# ----- SERVER STARTUP -----
# --- Server Execution Blocks ---
# For local development with Uvicorn (FastAPI's standard server)
if __name__ == '__main__':
    # The 'reload=True' flag enables hot-reloading for development
    uvicorn.run("app_fastapi:app", host='0.0.0.0', port=9021, reload=True)

