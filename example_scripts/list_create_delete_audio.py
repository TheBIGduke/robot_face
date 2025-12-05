
"""
@description: Simple script to list, create and delete an audio file via API endpoint.
Audios of 'face_server' with octybot voice.

@requirements: 'app_fastapi.py' (server), 'face.html' (octybot face with mouth on chromium) and 
'audioServer.py' MUST be running.
"""

import requests


# ----- SERVER CONFIGURATION -----
SERVER_IP = "localhost"
SERVER_PORT = "9021"
url_base = f"http://{SERVER_IP}:{SERVER_PORT}/v1/audio"


# *** List Audios ***
def list_audios():
    try:
        response = requests.get(url_base, json={}, params={}, timeout=2.0)
        response_body = response.json()

        if isinstance(response_body, list):
            # Use a list comprehension to extract the 'name' from each dictionary in the 'data' list
            message = [item.get('Name') for item in response_body if isinstance(item, dict) and 'Name' in item]
        else:
            print("Error: 'Name' key not found or not a list in the response.")
            message = []

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Server NOT available. {ex}"

    return message

# *** Create Audio ***
def create_audio(data):
    try:
        response = requests.post(url_base, json=data, timeout=2)
        message = response.text
    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return message

# *** Delete Audio ***
def delete_audio(data):
    try:
        response = requests.delete(url_base, json=data, timeout=2)
        message = response.text

    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return message


# ----- USAGE EXAMPLE -----
if __name__ == "__main__":

    # *** List of saved audios ***
    list_saved_audios = list_audios()

    print(f"No of audios: {len(list_saved_audios)}")
    
    if list_saved_audios is not None:
        print(list_saved_audios)


    # Create audio
    ## IMPORTANT: To generate an audio file for testing, use '@Test@' as 'Name'
    ## Audio file name will be: "Mood_Name.mp3"
    data = { # dummy audio dict
        "Mood": "Feliz",
        "Name": "prueba",
        "Text": "esto es una prueba de generación de audio"
    }

    message = create_audio(data)
    print("\nCreation message:", message)


    # Delete audio
    data1 = {
        "Name": "Triste_prueba" # full name used to remove file (with mood prefix)
    }

    # message1 = delete_audio(data1)
    # print("\nDelete message:", message1)