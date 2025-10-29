#!/bin/bash

sleep 15

# Process 3) face_server
cd ~/robot_face/face_server
python3 app_fastapi.py &
#gunicorn -w 4 -b 0.0.0.0:9020 -k uvicorn.workers.UvicornWorker 'app_fastapi:app' &

# Process 1) face_moods
sleep 3
cd ~/robot_face/face_moods
python3 audioServer.py &


# Process 2) Robot eyes and mouth (installed as debian package)

# Face configuration (at cd ~/robot_face/face_moods)
# To obtain displays position, use, $ xrandr
FACE_POSITION="1920,0" # Adjust X,Y coordinates as needed

sleep 5
chromium-browser \
    --kiosk \
    --window-position="${FACE_POSITION}" \
    "face.html"

