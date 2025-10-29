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

# Websocket server
uri = "ws://localhost:8760"

# A list of all available moods from your server files.
AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
]

# ----- Audio Management -----
# (Creation, Deletion, Playback, Get/Set Volume)
def post_audio(data):

	# 1. Calls file creation function
	response = t2s.createAudio(data)
	
	# 2. Check for the test name, using the correct key "Name"
	if data.get("Name") == "@Test@" and response:
		return {"Status": "Test"}
	
	# 3. Return status for non-test audio based on file creation success
	if response:
		return {"Status": True, "Description": "Audio file created/overwritten."}
	else:
		return {"Status": False, "Description": "Failed to create audio file. key.json missing?"}

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
	return t2s.eraseAudio(data["Name"])

# *** List Audios ***
def get_audios():
	base_dir = os.path.dirname(os.path.abspath(__file__))
	AUDIO_DIR = os.path.join(base_dir, "audios")

	if not os.path.exists(AUDIO_DIR):
		try:
			os.makedirs(AUDIO_DIR)
		except OSError:
			return []
		
	audio_files = []
	for filename in os.listdir(AUDIO_DIR):
		if filename.endswith(".mp3"):
			name = filename[:-4]
			audio_files.append({"Name": name})
	return audio_files


def set_volume(val):
    """
    Sets the absolute volume (e.g., '80') by passing the string directly to the amixer OS command.
    """
    # The string 'val' must contain the percentage
    os.system("amixer -D pulse sset Master " + val + "%")
    return {"Status": "Ok", "Volume": val}

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
            data = { "Status": True, "Value": int(current_volume) }
            return json.dumps(data)
        else:
            # Handle case where volume percentage couldn't be parsed
            error_data = { "Status": False, "Value": -1 }
            return json.dumps(error_data)

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        # Handle command failure or command not found
        error_data = {
            "Status": False,
            "Value": 0,
            "Description": f"Could not retrieve system volume: {e}"
        }
        return json.dumps(error_data)


# ----- MOODS -----

# *** List Available Moods ***
def get_moods():
    return AVAILABLE_MOODS

async def send_mood(command_type, mood):
	payload = {"type": command_type, **mood}
	try:
		async with websockets.connect(uri) as websocket:
			await websocket.send(json.dumps(payload)) # Converts the python dictionary payload into a JSON string
	except ConnectionRefusedError:
		print(f"Connection to {uri} refused. Is the audioServer.py running?")
	except Exception as e:
		print(f"An error occurred: {e}")


def set_mood(mood):
	asyncio.run(send_mood("mood", {"mood": mood}))
	return {"Status": "OK", "mood": mood}

def set_mouth(state):
	# state = "on", "off"
	asyncio.run(send_mood("audio", {"command": state}))
	return {"Status": "OK", "state": state}
