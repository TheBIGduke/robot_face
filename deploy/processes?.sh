#!/bin/bash

# Process 1) Gestor de Gestos, server to manage robot's audio
sleep 15
cd ~/robot_gesture/GestorGestos
./GestorGestos &

# Process 2) Robot eyes and mouth (installed as debian package)
sleep 5
gestosv6.1 &          # Select either 1 or 2, according to the monitor 

# Process 3) robot_audios_backend
sleep 6
cd ~/robot_gesture/robot_audios_backend
gunicorn -w 4 -b 0.0.0.0:9020 'app_fastapi:app'

