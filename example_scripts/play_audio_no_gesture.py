
"""
@description: Simple script to play a saved audio via endpoint, WITHOUT moving mouth.
To play another audio, a subprocess can be used.

@important: It is assumed that user wants to play an audio that was previously saved
and registered and the database of 'robot_audios_backend', WITHOUT moving octybot mouth.

@requirements: 'GestorGestos' (server), 'gestosv6.X' (octybot face with mouth) and 
'robot_audios_backend' (on port 9020) MUST be running.
"""

import requests, io
from time import time
from pydub import AudioSegment
from pydub.playback import play

SERVER_IP = "localhost"
SERVER_PORT = "9020"
saved_audio = "Nachos"


def play_audio_with_pydub(name):
    # Use the local IP and correct port
    base_path = "http://"+SERVER_IP+":"+SERVER_PORT+"/static/audios/"
    audio = name + ".mp3"
    timestamp = str(time())
    
    # 1. Construct the keyless URL to get the correct 206 streaming response
    full_url = base_path + audio + "?" + timestamp
    
    # 2. Add the 'Range' header to signal streaming intent (crucial for 206)
    headers = {'Range': 'bytes=0-'} 
    
    print(f"Requesting: {full_url}")

    try:
        # Fetch the audio file content
        # Using stream=True is a good practice for larger files
        response = requests.get(full_url, headers=headers, timeout=2, stream=True)

        if response.status_code == 206 or response.status_code == 200:
            print(f"Success! Status Code: {response.status_code}")
            
            # --- PYDUB PLAYBACK LOGIC ---
            
            # 3. Use io.BytesIO to wrap the raw audio content
            audio_data_io = io.BytesIO(response.content)
            
            # 4. Use pydub to load the audio from the in-memory byte stream.
            #    We explicitly tell pydub the format is 'mp3'.
            #    This step requires FFmpeg to be installed and accessible.
            audio_segment = AudioSegment.from_file(audio_data_io, format="mp3")
            
            print("Playing audio segment...")
            
            # 5. Play the audio segment
            play(audio_segment)
            
            print("Playback finished.")
            
        else:
            print(f"Failed to get audio. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except FileNotFoundError:
        print("\n*** ERROR: FFmpeg not found! ***")
        print("Please ensure FFmpeg is installed and added to your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred during playback: {e}")


if __name__ == '__main__' :
    # Call the function with your audio name
    play_audio_with_pydub(saved_audio)

