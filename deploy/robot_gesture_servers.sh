#!/bin/bash

sleep 15

# Process 2) face_moods
sleep 3
cd ~/robot_face/face_moods
python3 audioServer.py

# Process 1) face_server
cd ~/robot_face/face_server
python3 app_fastapi.py
