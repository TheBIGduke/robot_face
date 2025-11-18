
"""
@description: Simple script to play/stop a saved audio via API endpoint, WITH mouth moving.

@important: It is assumed that user wants to play an audio that was previously saved
and registered and the database of 'robot_audios_backend', WITH moving octybot mouth.

@requirements: 'GestorGestos' (server), 'gestosv6.X' (octybot face with mouth) and 
'robot_audios_backend' MUST be running.
"""

from time import time
import requests

SERVER_IP = "localhost"
SERVER_PORT = "9020"
saved_audio = "Saludo"

url_base = f"http://{SERVER_IP}:{SERVER_PORT}/v1/"


def play_audio(name):
    url = url_base + "play/"+name
    
    try:
        response = requests.get(url, timeout=2.0)
        message = response.json()

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"{ex}"

    return message


def stop_audio():
    url = url_base + "audio/pausa"
    
    try:
        response = requests.get(url, timeout=2.0)
        message = response.json()

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"{ex}"

    return message


# --- Usage example ---
if __name__ == "__main__":

    # Play audio
    response = play_audio(saved_audio)
    print(response)
    
    
    #Stop current audio
    import time
    time.sleep(2.0)
    print("After playing for 2 s, the audio is paused/stopped")
    stop_response = stop_audio()

    print("script finished")