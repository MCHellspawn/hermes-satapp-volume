#!/bin/bash

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
USER=$(who)
read -p "Enter MQTT Hostname: " MQTT_HOST
read -p "Enter MQTT Port:" -i "1833" MQTT_PORT
read -p "Enter MQTT User:" MQTT_USER
read -p "Enter MQTT Password:" MQTT_PASS
echo $SCRIPTPATH

# Create the app path and move the files
mkdir -p /usr/lib/rhasspy-skills/satapp-volume
cp -r $SCRIPTPATH/* /usr/lib/rhasspy-skills/satapp-volume
cd /usr/lib/rhasspy-skills/satapp-volume

# Create and activate the python virtual environment
python3 -m venv satapp-volume
source satapp-volume/bin/activate

# Install dependancies in virtual environment
pip3 install -r requirements.txt

# Deactivate the pyton virtual environment
deactivate

# Remove existing service definition
sudo rm -f /lib/systemd/system/rhasspy.skill.volume.service

# Create new service definition
touch /lib/systemd/system/rhasspy.skill.volume.service
:> /lib/systemd/system/rhasspy.skill.volume.service

echo "
[Unit]
Description=Rhasspy Volume Skill
After=multi-user.target

[Service]
Type=simple
User=$USER
ExecStart=/bin/bash -c 'cd /usr/lib/rhasspy-skills/satapp-volume && source satapp-volume/bin/activate && python3 hermes-app-volume.py --host "$MQTT_HOST" --username "$MQTT_USER" --password "$MQTT_PASS" --port "$MQTT_PORT"'
Restart=on-abort

[Install]
WantedBy=multi-user.target

  " >>  /lib/systemd/system/rhasspy.skill.volume.service

# Make app script executable
chmod +x hermes-app-volume.py

# Set perms on service definition and start it
sudo sudo chmod 644 /lib/systemd/system/rhasspy.skill.volume.service
sudo systemctl stop rhasspy.skill.volume.service
sudo systemctl daemon-reload
sudo systemctl enable rhasspy.skill.volume.service
sudo systemctl start rhasspy.skill.volume.service
#sudo reboot