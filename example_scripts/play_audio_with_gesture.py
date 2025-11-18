
"""
@description: Simple script to test audio operations via API endpoint, WITH mouth moving.

@important: by default, robot mouth will move for any audio of the system.

@requirements: 'app_fastapi.py' (server), 'face.html' (octybot face with mouth on chromium) and 
'audioServer.py' MUST be running.
"""

import time, requests

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
    url = url_base + "audio/stop"
    
    try:
        response = requests.get(url, timeout=2.0)
        message = response.json()

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"{ex}"

    return message


def get_volume():
    url = url_base + "audio/volume"
    
    try:
        response = requests.get(url, timeout=2.0)
        message = response.json()

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"{ex}"

    return message

def set_volume(val):
    url = url_base + f"audio/volume/{val}"
    
    try:
        response = requests.post(url, timeout=2.0)
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
    time.sleep(2.0)
    print("After playing for 2 s, the audio is stopped")
    stop_response = stop_audio()
    print(stop_response)

    get_volume_response = get_volume()
    print("Current system volume:", get_volume_response)

    set_volume_response = set_volume(50) # volume 0-100
    print("Set system volume:", set_volume_response)

    print("script finished")