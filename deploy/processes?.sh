#!/bin/bash

# --- Configuration ---
# Set the absolute paths to your project directories
PROJECT_ROOT="$HOME/robot_gesture"
FACE_MOODS_DIR="$PROJECT_ROOT/robot_face/face_moods" # Assumed path
BACKEND_DIR="$PROJECT_ROOT/robot_audios_backend"
GESTOR_DIR="$PROJECT_ROOT/GestorGestos"

# Face configuration (from octopid.sh)
FACE_HTML_FILE="file://${FACE_MOODS_DIR}/face.html"
FACE_POSITION="0,0" # Adjust X,Y coordinates as needed

# --- Process IDs ---
# We store PIDs to ensure we only kill our own processes
PID_GUNICORN=
PID_GESTOR=
PID_AUDIO_SERVER=
PID_CHROMIUM=

# --- Cleanup Function ---
# This function is called when the script receives an EXIT or INT signal
cleanup() {
    echo -e "\nShutting down all processes..."

    # Kill processes by their stored PIDs
    # The '-' in front of the PID kills the entire process group
    [ ! -z "$PID_GUNICORN" ] && echo "Stopping Gunicorn (PID: $PID_GUNICORN)" && kill -TERM -$PID_GUNICORN 2>/dev/null
    [ ! -z "$PID_AUDIO_SERVER" ] && echo "Stopping Audio Server (PID: $PID_AUDIO_SERVER)" && kill -TERM -$PID_AUDIO_SERVER 2>/dev/null
    [ ! -z "$PID_CHROMIUM" ] && echo "Stopping Chromium (PID: $PID_CHROMIUM)" && kill -TERM -$PID_CHROMIUM 2>/dev/null
    
    # Fallback: pkill for any stragglers
    pkill -f "gunicorn.*app_fastapi:app"
    pkill -f "python3 ${FACE_MOODS_DIR}/audioServer.py"
    
    echo "Cleanup complete. Exiting."
    exit 0
}

# Trap signals to trigger the cleanup function
# INT (Ctrl+C), TERM (kill), EXIT (script finishing)
trap cleanup INT TERM EXIT

# 2. Start robot_audios_backend (Gunicorn)
echo "Starting FastAPI backend (Gunicorn)..."
cd "$BACKEND_DIR"
gunicorn -w 4 -b 0.0.0.0:9020 'app_fastapi:app' &
PID_GUNICORN=$(jobs -p | tail -n 1)

# 3. Start the Face WebSocket Audio Server
echo "Starting Face Audio Server..."
cd "$FACE_MOODS_DIR"
python3 audioServer.py &
PID_AUDIO_SERVER=$(jobs -p | tail -n 1)

# Give servers a moment to initialize
echo "Waiting 5 seconds for servers to start..."
sleep 5

# 4. Start the Face UI (Chromium Kiosk)
echo "Starting Chromium face in kiosk mode at ${FACE_POSITION}..."
chromium-browser \
    --kiosk \
    --window-position="${FACE_POSITION}" \
    "${FACE_HTML_FILE}" &
PID_CHROMIUM=$(jobs -p | tail -n 1)

echo "All processes started."
echo "Press Ctrl+C to stop all services."

# Wait indefinitely. The 'trap' will handle the exit.
wait