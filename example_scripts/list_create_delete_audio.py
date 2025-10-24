
"""
@description: Simple script to list, create and delete an audio via API endpoint.
Audios of 'robot_audios_backend' server with octybot voice.

@requirements: 'GestorGestos' (server), 'gestosv6.X' (octybot face with mouth) and 
'robot_audios_backend' MUST be running.
"""

import requests

SERVER_IP = "localhost"
SERVER_PORT = "9020"
url_base = f"http://{SERVER_IP}:{SERVER_PORT}/v1/audio"


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


def create_audio(data):
    try:
        response = requests.post(url_base, json=data, timeout=2)
        # status_code = response.status_code
        message = response.text
    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return message


def delete_audio(data):
    try:
        response = requests.delete(url_base, json=data, timeout=2)

        # status_code = response.status_code
        message = response.text

    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return message


# --- Usage example ----
if __name__ == "__main__":

    # List of saved audios
    list_saved_audios = list_audios()

    print(f"No of audios in db: {len(list_saved_audios)}")
    
    if list_saved_audios is not None:
        print(list_saved_audios)


    # Create audio
    data = { # dummy audio dict
        "Name": "@Test@",
        "Text": "esto es una prueba de generación de audio"
    }

    message = create_audio(data)
    print("\nCreation message:", message)

    ## IMPORTANT: To generate an audio file omitting its register in database, 
    # use '@Test@' as 'Name'


    # Delete audio
    data1 = {
        "id": 2, # id used to remove in db
        "Name": "mi_prueba" # name used to remove file
    }

    # message1 = delete_audio(data1)
    # print("\nDelete message:", message1)

