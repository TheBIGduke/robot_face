import lib.db as db
import json
import asyncio
import websockets
import json
import os

# A list of all available moods from your server files.
AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
]

# ----- Audio Management -----
# (Creation, Deletion, Playback)
def post_audio(data):
	import lib.t2s as t2s
	response = t2s.createAudio(data)
	if (data["Name"] != "@Test@"):
		return {"Status": "Test"}
	if response:
		return {"Status": True, "Description": "Audio file created/overwritten."}
	else:
		return {"Status": False, "Description": "Failed to create audio file."}

def delete_audio(data):
		import lib.t2s as t2s
		return t2s.eraseAudio(data["Name"])

def get_audios():
	AUDIO_DIR = "lib/audios/"

	if not os.path.exists(AUDIO_DIR):
		try:
			os.makedirs(AUDIO_DIR)
		except OSError:
			return []
		
	audio_files = []
	for filename in os.listdir(AUDIO_DIR):
		if filename.endswith(".mp3"):
			name = filename[:-4]
			audio_files.append({"Nombre": name, "Texto": "N/A (Local File)"})
	return audio_files

def volume(val):

    os.system("amixer -D pulse sset Master " + val + "%")
    db.update_volume({"Value":val})
    return {"Status": "Ok", "Volume":val}

def volumeAdd(val):
    return db.add_volume(val)

def get_volume():
    return db.get_volume()

def update_volume(val):
    return db.update_volume(val)

def pausa():
	import os
	os.system("pkill mpg321")
	return {"Status": "Ok", "mpg321": "Kill" }


# ----- Moods -----
def get_moods():
	return AVAILABLE_MOODS


async def send_command(websocket, command_type, params):
    """Sends a JSON command to the WebSocket server."""
    # JSON payload
    payload = {"type": command_type, **params}
    await websocket.send(json.dumps(payload)) # Converts the python dictionary payload into a JSON string and sends it over the server
    print(f"Sent command: {payload}")

async def send_mood(uri, mood):
	try:
		async with websockets.connect(uri) as websocket:
			await send_command(websocket, "mood", {"mood": mood})
	except ConnectionRefusedError:
		print(f"Connection to {uri} refused. Is the audioServer.py running?")
	except Exception as e:
		print(f"An error occurred: {e}")

def set_mood(mood):
	uri = "ws://localhost:8760" # Server connection (adjust if needed)
	asyncio.run(send_mood(uri, mood))

	return {"Status": "OK", "mood": mood}