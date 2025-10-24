import os
from time import time

def createAudio(data):
    from google.cloud import texttospeech

    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='lib/data/key.json'
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()
    #____________________________PARAMETROS_________________________________

    name="es-US-Wavenet-B" #Voz es-US-Wavenet-C (A, B o C), es-US-Standard-A (A,B o C)
    language_code="es-US"

    audio_encoding=texttospeech.AudioEncoding.MP3
    speaking_rate = 0.9
    pitch = 8

    #__________________________________________________________________________

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

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    # FIXED: Save to the simplified path: "lib/audios/"
    with open("lib/audios/" + data["Name"] + ".mp3", "wb") as out: 
        # Write the response to the output file.
        out.write(response.audio_content)

    return True

def eraseAudio(Name):
    try:
        # FIXED: Delete from the simplified path: "lib/audios/"
        os.remove('lib/audios/' + Name + ".mp3")
    except FileNotFoundError as e:
        print(e)
    return {"Status" : "Deleted"}

def playAudio(name):
    from websockets.sync.client import connect

    aux = str(time())

    with connect("ws://localhost:8760") as websocket:
        websocket.send("Audios")
        websocket.send("http://localhost:9020/static/" + name + ".mp3?"+aux) # URL path adjusted to reflect new mount point
        websocket.close()

def pausa():
    from websockets.sync.client import connect

    with connect("ws://localhost:8760") as websocket:
        websocket.send("Audios")
        websocket.send("stop")
        websocket.close()

    return {"Status": "Ok", "audio": "pause" }