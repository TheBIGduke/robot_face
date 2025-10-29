
"""
@description: A WebSocket server that streams system audio FFT data (bass levels)
to connected clients and allows for real-time control (mood changes, audio on/off)
via a background terminal input thread.
"""

import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque
import threading
import time
import sys

# --- THIS IS A CODE THAT RUNS THE WEBSOCKET SERVER AND ALLOWS TO CHANGE STATES BY USING THE TERMINAL INPUT ---

# ----- CONFIGURATION & GLOBALS -----
# Central list of all valid moods, synchronized with the HTML file
AVAILABLE_MOODS = (
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
)

# *** Global state trackers ***
ACTIVE_CONNECTIONS = set()
initial_connection_made = False
is_audio_enabled = False

# *** Audio settings ***
sampleRate = 44100
chunkSize = 1024
bassRangeStart, bassRangeEnd = 60, 250
midRangeStart, midRangeEnd = 251, 2000
highRangeStart, highRangeEnd = 2001, 6000


# ----- WEBSOCKET HANDLERS & HELPERS -----

# *** Handle New Client Connection ***
async def audioStreamHandler(websocket):
    global initial_connection_made
    if not initial_connection_made:
        initial_connection_made = True

    ACTIVE_CONNECTIONS.add(websocket)
    try:
        await process_audio(websocket)
    finally:
        if websocket in ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS.remove(websocket)

# *** Process and Stream Audio FFT ***
async def process_audio(websocket):
    global is_audio_enabled
    bass_history = deque(maxlen=5)
    try:
        with sc.get_microphone(
            id=str(sc.default_speaker().name),
            include_loopback=True
        ).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                if not is_audio_enabled:
                    await asyncio.sleep(0.1)
                    continue

                data = mic.record(numframes=chunkSize)
                if data.size == 0: continue

                # ... FFT analysis ...
                fftData = np.fft.rfft(data[:, 0])
                fftFreq = np.fft.rffreq(len(data[:, 0]), 1.0 / sampleRate)
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))
                bassEnergy = np.mean(np.abs(fftData[bassIndices])) if bassIndices[0].size > 0 else 0
                
                # ... Normalization and smoothing ...
                normalizedBass = min(bassEnergy / 30.0, 1.0)
                bass_history.append(normalizedBass)
                smoothed_bass = np.mean(bass_history)
                
                payload = {"type": "audio", "bass": smoothed_bass}
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(0.01)

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Audio processing error: {e}")
        pass # Allow the handler to clean up

# *** Send Mood Command ***
async def sendMood(websocket, mood_name):
    try:
        payload = {"type": "mood", "mood": mood_name}
        await websocket.send(json.dumps(payload))
    except websockets.exceptions.ConnectionClosed:
        pass

# *** Send Audio Off Signal ***
async def send_audio_off_signal(websocket):
    try:
        payload = {"type": "audio", "bass": 0}
        await websocket.send(json.dumps(payload))
    except websockets.exceptions.ConnectionClosed:
        pass


# ----- TERMINAL INPUT THREAD -----

# *** Print Help Menu ***
def print_help_menu(options_text):
    print(f"\n--- Available Commands ---\nMoods: {options_text}\nActions: audio on, audio off\nType 'exit' to quit.")

# *** Handle Terminal Input (Background Thread) ***
def terminal_input_loop(loop):
    global is_audio_enabled
    options_text = ", ".join(AVAILABLE_MOODS)
    loader_chars = ['|', '/', '-', '\\']

    while True:
        # ... Handle connection status display ...
        if not ACTIVE_CONNECTIONS:
            i = 0
            message = "Connection lost. Reconnecting... " if initial_connection_made else "Waiting for client connection... "
            sys.stdout.write("\r" + " " * 80 + "\r")
            while not ACTIVE_CONNECTIONS:
                print(f"\r{message}{loader_chars[i % len(loader_chars)]}", end="")
                sys.stdout.flush()
                i += 1
                time.sleep(0.2)
            
            print(f"\rClient connected! You can now send commands.      ")
            print_help_menu(options_text)
            
        if not ACTIVE_CONNECTIONS:
            # Should not reach here, but as a safeguard
            time.sleep(0.5) 
            continue

        # ... Get command input from the user ...
        try:
            command = input("Enter command: ").strip().lower()
        except EOFError:
            # Handle Ctrl+D
            command = 'exit'
        except KeyboardInterrupt:
            # Handle Ctrl+C (let the main thread handle the global exit)
            return 
        
        if command == 'exit':
            print("\nExiting command loop.")
            # Use sys.exit to shut down the program gracefully
            return 

        # ... Audio on ...
        elif command == 'audio on':
            if not is_audio_enabled:
                is_audio_enabled = True
                print("--> Audio streaming ENABLED.")
            else:
                print("--> Audio streaming is already ON.")

        # ... Audio off ...
        elif command == 'audio off':
            if is_audio_enabled:
                is_audio_enabled = False
                print("--> Audio streaming DISABLED. Sending reset signal.")
                # Send the zero-bass signal in the async loop
                futures = [
                    asyncio.run_coroutine_threadsafe(send_audio_off_signal(ws), loop)
                    for ws in list(ACTIVE_CONNECTIONS)
                ]
                # Wait for the coroutines to complete before proceeding
                for future in futures: future.result()
            else:
                print("--> Audio streaming is already OFF.")

        elif command in AVAILABLE_MOODS:
            print(f"--> Sending command: '{command}'")
            # Send the mood command in the async loop
            futures = [
                asyncio.run_coroutine_threadsafe(sendMood(ws, command), loop)
                for ws in list(ACTIVE_CONNECTIONS)
            ]
            # Wait for the coroutines to complete before proceeding
            for future in futures: future.result()

        elif command:
            print(f"Error: '{command}' is not a valid command.")
            print_help_menu(options_text)

        # Clear command variable for next loop iteration
        command = None 


# ----- SERVER STARTUP -----

# *** Main Async Server Function ***
async def mainAsync():
    serverAddress = "localhost"
    serverPort = 8760
    print(f"Starting WebSocket server on ws://{serverAddress}:{serverPort}")

    # The terminal input loop needs access to the running loop
    loop = asyncio.get_running_loop()
    input_thread = threading.Thread(target=terminal_input_loop, args=(loop,), daemon=True)
    input_thread.start()

    async with websockets.serve(audioStreamHandler, serverAddress, serverPort):
        # Keep the main async loop running indefinitely
        await asyncio.Future()

# *** Entry Point ***
if __name__ == "__main__":
    try:
        asyncio.run(mainAsync())
    except KeyboardInterrupt:
        print("\nServer stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")