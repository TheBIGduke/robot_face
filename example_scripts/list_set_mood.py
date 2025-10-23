
"""
ACTUALIZAR----
@description: Simple script to list, create and delete an audio via API endpoint.
Audios of 'robot_audios_backend' server with octybot voice.

@requirements: 'GestorGestos' (server), 'gestosv6.X' (octybot face with mouth) and 
'robot_audios_backend' MUST be running.
"""

import requests

SERVER_IP = "localhost"
SERVER_PORT = "9020"
url_base = f"http://{SERVER_IP}:{SERVER_PORT}/v1/moods"


def list_moods():
    try:
        message = []

        response = requests.get(url_base, json={}, params={}, timeout=2.0)
        response_body = response.json()

        print(response_body)
        message = response_body

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Server NOT available. {ex}"

    return message

def set_mood():
    try:
        response = requests.post(url_base+"/sad", json={}, params={}, timeout=2.0)
        response_body = response.json()

        # print(response_body)

        message = response_body

    except requests.exceptions.Timeout:
        message = "The request timed out after 2 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Server NOT available. {ex}"

    return message

# --- Usage example ----
if __name__ == "__main__":

    list_moods = list_moods()

    set_res = set_mood()
    print("set mood response:", set_res)



    