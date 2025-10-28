"""
@description: Backend service that manages the phrases audio files (create, delete, list), controls system volume using amixer commands,
and sends "mood" updates (like 'happy' or 'sad') to a WebSocket server, to sync with the face visualizer.
"""

import json
import asyncio
import websockets
import os
import subprocess
import re
import lib.t2s as t2s


# list of all available moods
AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
]


# ----- AUDIO MANAGEMENT -----
# (Creation, Deletion, Playback)

# *** Creation ***
def post_audio(data):

    # Calls file creation function
    response = t2s.createAudio(data)
    
    # Check for the test name, using the correct key "Name"
    if data.get("Name") == "@Test@":
        return {"Status": "Test"}
    
    # Return status for non-test audio based on file creation success
    if response:
        return {"Status": True, "Description": "Audio file created/overwritten."}
    else:
        return {"Status": False, "Description": "Failed to create audio file."}

# *** Deletion ***
def delete_audio(data):
        # Use the correct key "Name" to pass the audio name to the erase function
        return t2s.eraseAudio(data["Name"])

# *** List Audios ***
def get_audios():
    # Searches for the directory where they're stored
    base_dir = os.path.dirname(os.path.abspath(__file__))
    AUDIO_DIR = os.path.join(base_dir, "audios")

    # If the directory does not exist, it's created
    if not os.path.exists(AUDIO_DIR):
        try:
            os.makedirs(AUDIO_DIR)
        except OSError:
            return []

    # Filters and lists all .mp3 files in the directory 
    audio_files = []
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith(".mp3"):
            name = filename[:-4]
            audio_files.append({"Name": name, "Text": "N/A (Local File)"})
    return audio_files


# ----- VOLUME MANAGEMENT -----

# *** Set Volume ***
def volume(val):
    # The string 'val' must contain the percentage or the relative sign (+/-).
    os.system("amixer -D pulse sset Master " + val + "%")
    return {"Status": "Ok", "Volume":val}

# *** Set Volume (from POST) ***
def volumeAdd(data):
    """
    Handles volume addition/setting via a POST body (e.g., {"Value": "+5"}).
    It delegates the actual setting to the primary volume function.
    """
    try:
        # Assumes input is a dictionary like {"Value": "80"} or {"Value": "+5"}
        volume_value = str(data["Value"])
        return volume(volume_value)
    except KeyError:
        return {"Status": False, "Description": "Missing 'Value' key in payload."}
    except Exception as e:
        return {"Status": False, "Description": f"Error setting volume: {e}"}

# *** Get Current Volume ***
def get_volume():
    """
    Retrieves the actual system volume level using the amixer command.
    """
    try:
        # Run amixer command and capture output
        result = subprocess.run(
            ['amixer', '-D', 'pulse', 'get', 'Master'],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        # Use regex to find the volume percentage value, e.g., [90%]
        match = re.search(r'\[(\d+)%\]', output)
        
        if match:
            # Extract the volume value (e.g., '90')
            current_volume = match.group(1)
            
            # Format the actual volume into the required JSON string
            data = {
                "Status": True,
                "Value": int(current_volume),
                "Description": "Actual system volume retrieved"
            }
            return json.dumps(data)
        else:
            # Handle case where volume percentage couldn't be parsed
            error_data = {
                "Status": False,
                "Value": 0,
                "Description": "Could not parse volume from amixer output"
            }
            return json.dumps(error_data)

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        # Handle command failure or command not found
        error_data = {
            "Status": False,
            "Value": 0,
            "Description": f"Could not retrieve system volume: {e}"
        }
        return json.dumps(error_data)

# *** Update Volume (from PUT) ***
def update_volume(data):
    try:
        # Assumes input is a dictionary like {"Value": "80"} or {"Value": "-10"}
        volume_value = str(data["Value"])
        return volume(volume_value)
    except KeyError:
        return {"Status": False, "Description": "Missing 'Value' key in payload."}
    except Exception as e:
        return {"Status": False, "Description": f"Error setting volume: {e}"}

# *** Pause Audio Playback ***
def pause():
    os.system("pkill mpg321")
    return {"Status": "Ok", "mpg321": "Kill" }


# ----- MOODS -----

# *** List Available Moods ***
def get_moods():
    return AVAILABLE_MOODS

# *** Send WebSocket Command ***
async def send_command(websocket, command_type, params):
    # JSON payload
    payload = {"type": command_type, **params}
    await websocket.send(json.dumps(payload)) # Converts the python dictionary payload into a JSON string and sends it over the server
    print(f"Sent command: {payload}")

# *** Send Mood (Async) ***
async def send_mood(uri, mood):
    try:
        async with websockets.connect(uri) as websocket:
            await send_command(websocket, "mood", {"mood": mood})
    except ConnectionRefusedError:
        print(f"Connection to {uri} refused. Is the audioServer.py running?")
    except Exception as e:
        print(f"An error occurred: {e}")

# *** Set Mood (Wrapper) ***
def set_mood(mood):
    uri = "ws://localhost:8760" # Server connection (adjust if needed)
    asyncio.run(send_mood(uri, mood))

    return {"Status": "OK", "mood": mood}