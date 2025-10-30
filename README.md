# ROBOT_FACE

This repository contains the 3 micro-services to deploy the Octopy's robot face with mouth motion.

## Summary

The micro-services are:

+ 1) face_server

Backend to manage audio functionalities. Audios using Octybot voice.

+ 2) face_moods

Websocket server to set robot face and to split audio frequencies to move robot mouth.

+ 3) face.html (open it with Chromium)

Robot face (eyes and mouth).


**Note:** For simplicity, 'deploy/robot_gesture.sh' runs all 3 sub-process in once.


## Pre-requisites

```bash
sudo apt update
sudo apt-get install chromium-browser
cd robot_face
pip install -r requirements.txt
```

If "DISPLAY" environment variable is not set in '~/.bashrc' file, add it with:

`export DISPLAY=:0`


## Cloning this repo

```
cd ~
git clone git@springlabsdevs.net:mecatronica/robotica/robot_face.git
```

**Important:** To generate audios with Octybot voice, user MUST add the 'key.json' file at "~/robot_face/face_server/lib/data".


## Start the functionality

```
cd ~/robot_face/deploy
./robot_gesture.sh
```


## Examples of use

In 'example_script' some python scripts are stored to show some basic examples of use via API endpoints.


