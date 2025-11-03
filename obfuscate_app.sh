#!/bin/bash

#To run this script
# $ sudo chmod +x obfuscate_app.sh && ./obfuscate_app.sh {debug,release}

# Define the package name you want to check (only for one pkg)
PACKAGE_NAME="pyarmor"

# Use 'pip show' to check for the package.
# The exit status is what we are interested in:
# 0 if the package is found, and non-zero otherwise.
pip show "${PACKAGE_NAME}" > /dev/null 2>&1

# Check the exit status of the previous command ($?)
if [ $? -eq 0 ]; then
    echo "${PACKAGE_NAME} is already installed."
else
    echo "${PACKAGE_NAME} is NOT installed."
    pip install "${PACKAGE_NAME}"
fi


info() { #Function to print a message ">>>" in blue color
    echo -e "\n\e[34m>>>\e[0m ${@}"
}


if [ "$1" = "release" ]; then
    info "Obfuscating application in release mode. Source files will be deleted!!!"
elif [ "$1" = "debug" ]; then
    info "Obfuscating application in debug mode (copy of source files)"
    # backup app directory
    cp -r ~/robot_face/ ~/robot_face_bk/
elif [ "$1" = "usage" ] || [ "$1" = "help" ]; then
    info "Usage:\n./obfuscate_app.sh {debug,release}\n  debug: copy source files\n  release: delete source files"
    exit
else
    info "Mode required. For details, type $ ./obfuscate_app.sh usage"
    exit
fi

sleep 2

# obfuscate app
pyarmor gen .
# Only python scripts are obfustaed at dist folder

# Create a temporal directory
mkdir ~/app_temp
cd dist/

# copy required content of the application (dist folder for python and other files) to the temporal root app dir
cp -r * ~/app_temp/
rm -r  ~/app_temp/example_scripts #remove examples
cp ~/robot_face/face_moods/face.html ~/app_temp/face_moods/face.html
cp -r ~/robot_face/deploy ~/app_temp/deploy

cp -r ~/robot_face/face_server/lib/audios ~/app_temp/face_server/lib/audios
cp -r ~/robot_face/face_server/lib/data ~/app_temp/face_server/lib/data

# Copy 'pyarmor_runtime_000000' folder inside both micro-services (for this case)
cp -r ~/app_temp/pyarmor_runtime_000000 ~/app_temp/face_moods/pyarmor_runtime_000000
cp -r ~/app_temp/pyarmor_runtime_000000 ~/app_temp/face_server/pyarmor_runtime_000000
rm -r ~/app_temp/pyarmor_runtime_000000

cd ../../

# remove original files
rm -rf robot_face/
mv app_temp/ robot_face/
cd ~
info "robot_face obfuscated successfully"



