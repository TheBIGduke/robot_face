
"""
@description: Library for handling Text-to-Speech (TTS) generation using Google Cloud
and controlling audio playback (play/pause) by sending commands to a WebSocket server.
"""

import os
from time import time
from websockets.sync.client import connect
from google.cloud import texttospeech


# ----- CREATE AUDIO FILE -----
# (Google TTS)
def createAudio(data):

    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='lib/data/key.json'
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # *** TTS Parameters ***
    name="es-US-Wavenet-B"
    language_code="es-US"
    audio_encoding=texttospeech.AudioEncoding.MP3
    speaking_rate = 0.9
    pitch = 8

    # *** Sintezise Speech Request ***
    synthesis_input = texttospeech.SynthesisInput(text=data["Text"])

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        name=name, language_code=language_code
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=audio_encoding, speaking_rate = speaking_rate, pitch = pitch
    )

    # Perform the request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save to the pahth: "lib/audios/"
    with open("lib/audios/" + data["Name"] + ".mp3", "wb") as out: 
        # Write the response to the output file.
        out.write(response.audio_content)

    return True

# ----- Erase Audio File -----
def eraseAudio(Name):
    try:
        # Delete from the path: "lib/audios/"
        os.remove('lib/audios/' + Name + ".mp3")
    except FileNotFoundError as e:
        print(e)
    return {"Status" : "Deleted"}

# ----- Play Audio (via WebSocket) -----
def playAudio(name):
    aux = str(time())

    with connect("ws://localhost:8760") as websocket:
        websocket.send("Audios")
        websocket.send("http://localhost:9020/static/" + name + ".mp3?" + aux)
        websocket.close()

# ----- Pause Audio (via WebSocket) -----
def pause():
    with connect("ws://localhost:8760") as websocket:
        websocket.send("Audios")
        websocket.send("stop")
        websocket.close()

    return {"Status": "Ok", "audio": "pause" }