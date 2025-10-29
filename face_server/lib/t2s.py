
"""
@description: Library for handling Text-to-Speech (TTS) generation using Google Cloud
and controlling audio playback (play/pause) by sending commands to a WebSocket server.
"""

import os
from google.cloud import texttospeech
import subprocess

audios_dir = "lib/audios/"
subprocess_pointer = None

def createAudio(data):
    google_key_file = 'lib/data/key.json'

    if os.path.exists(google_key_file):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']=google_key_file
    else:
        print("\n--- Error: text to speech Google key file DOES NOT exist ---\n")
        return False
    
    client = texttospeech.TextToSpeechClient() # Instantiates a client

    # *** TTS Parameters ***
    name="es-US-Wavenet-B"
    language_code="es-US"
    audio_encoding=texttospeech.AudioEncoding.MP3
    speaking_rate = 0.9
    pitch = 8

    # Set the text input to be synthesized
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

    # The response's audio_content is binary.
    with open(audios_dir + data["Name"] + ".mp3", "wb") as out: 
        out.write(response.audio_content) # Write the response to the output file.

    return True

# ----- Erase Audio File -----
def eraseAudio(Name):
    try:
        os.remove(audios_dir + Name + ".mp3")
    except FileNotFoundError as e:
        print(e)
    return {"Status" : "Deleted"}

def playAudio(audio_file):
    global subprocess_pointer
    path_file = audios_dir + audio_file + ".mp3"
    cmd = ["cvlc","--fullscreen","--noloop","--no-video-title-show","--video-on-top",path_file]
    
    subprocess_pt = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    subprocess_pointer = subprocess_pt
    return {"Status": "Ok", "audio": "playing"}


def stop():
    global subprocess_pointer
    if subprocess_pointer is not None:
        subprocess_pointer.kill()
    return {"Status": "Ok", "audio": "stopped"}
