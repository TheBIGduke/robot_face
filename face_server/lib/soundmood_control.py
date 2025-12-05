"""
@description: Backend service that manages the phrases audio files (create, delete, list), 
controls system volume using amixer commands, and sends "mood" updates (like 'Feliz' or 'Triste') 
to a WebSocket server, to sync with the face visualizer.
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
# IMPORTANT: AVAILABLE_MOODS ARE DEFINED IN "face_moods/audioServer.py" and "face.html" AS WELL
AVAILABLE_MOODS = (
    'Neutral', 'Feliz', 'Triste', 'Enojado', 'Sorprendido', 'Asustado', 'Mareado',
    'Preocupado', 'Dudoso', 'Inocente', 'Guiñando', 'Enamorado', 'Decepcionado'
)


# ----- Audio Management -----
# (Creation, Deletion, Playback, Get/Set Volume)

# *** Creation ***
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
		return {"Status": False, "Description": "Failed to create audio file. key.json missing or invalid?"}

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
		if filename.find("@Test@") > -1:
			os.remove(AUDIO_DIR+"/"+filename)
			print(f"{filename} removed since it is a test audio")
			continue
		if filename.endswith(".mp3"):
			name = filename[:-4]
			audio_files.append({"Name": name})
	return audio_files


# ----- VOLUME MANAGEMENT -----
# *** Set Volume ***
def set_volume(val):
    """
    Sets the absolute volume in percentage by passing the string directly to the amixer OS command.
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
            return { "Status": True, "Value": int(current_volume) }
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


# ----- Moods -----
# *** List Available Moods ***
def get_moods():
	return AVAILABLE_MOODS


# *** Send WebSocket Command ***
async def send_mood(command_type, mood):
	payload = {"type": command_type, **mood} # JSON payload
	try:
		async with websockets.connect(uri) as websocket:
			await websocket.send(json.dumps(payload)) # Converts the python dictionary payload into a JSON string
	except ConnectionRefusedError:
		print(f"Connection to {uri} refused. Is the audioServer.py running?")
	except Exception as e:
		print(f"An error occurred: {e}")

# *** Set Mood (Wrapper) ***
def set_mood(mood):
	asyncio.run(send_mood("mood", {"mood": mood}))
	return {"Status": "OK", "mood": mood}

# *** Set the mouth state (Wrapper). state = "on", "off" ***
def set_mouth(state):
	asyncio.run(send_mood("audio", {"command": state}))
	return {"Status": "OK", "state": state}