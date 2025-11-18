
"""
@description: Simple script to list and to set mood of robot face via API endpoint.

@requirements: 'app_fastapi.py' (server), 'face.html' (octybot face with mouth on chromium) and 
'audioServer.py' MUST be running.
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



    