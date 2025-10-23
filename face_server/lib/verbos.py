import lib.db as db
import json
import asyncio
import websockets
import json

# A list of all available moods from your server files.
AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
]

#CRUD Audios
def post_audio(data):
	import lib.t2s as t2s
	response = t2s.crearAudio(data)
	if response and (data["Nombre"] != "@Test@"):
		return db.post_audio(data)
	else:
		return {"Status": "Test"}

def delete_audio(data):
	response1 = db.delete_audio({"id" : data["id"]})
	if response1["Status"]:
		import lib.t2s as t2s
		return t2s.borrarAudio(data["Nombre"])
	return response1

def get_audios():
	return db.get_audios()

def volume(val):
    import os
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


# Moods
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