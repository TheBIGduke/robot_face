# ROBOT_FACE

This repository contains the 3 micro-services to deploy the Octopy's robot face with mouth motion.

The micro-services are:

+ 1) face_moods

Websocket server to set robot face and to split audio frequencies to move robot mouth.
cd ~/robot_face/face_moods
python3 audioServer.py


+ 2) face.html (open it with Chromium)

Robot face (eyes and mouth).



+ 3) face_server

Backend to manage audio functionalities. Audios using Octybot voice.

**Note:** For simplicity, 'deploy/robot_gesture.sh' runs all 3 sub-process in once.


## Cloning this repo

```
cd ~
git clone git@springlabsdevs.net:mecatronica/robotica/robot_face.git
```

## Pre-requisites

```bash
sudo apt-get install chromium-browser
```


## Robot gesture setup

```
cd ~/robot_face
./robot_face_installer.sh
```

## Start the functionality

```
cd ~/robot_face/deploy
./robot_gesture.sh
```


## Examples of use

In 'example_script' some python scripts are stored to show some basic examples of use via API endpoints.


