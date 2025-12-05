#!/bin/bash

cd ~/robot_face/face_moods

# Face configuration (at cd ~/robot_face/face_moods)
# To obtain displays position, use, $ xrandr
FACE_POSITION="1920,0" # Adjust X,Y coordinates as needed

sleep 5
chromium-browser \
    --kiosk \
    --window-position="${FACE_POSITION}" \
    "face.html"

