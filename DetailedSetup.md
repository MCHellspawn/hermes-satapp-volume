# Step-by-step Setup Instructions

Assumes you have a working Linux server with a working Docker installation.

1. Login to a Linux server with Docker installed, make sure this server has access to the same network as Rhasspy.
2. Create a folder to work from for the install and navigate into it.
```bash
mkdir time-skill
cd time-skill 
```
3.  Clone the git repo
```bash
git clone https://github.com/MCHellspawn/hermes-app-time.git
```
4. Build the docker image, this is just the image the container will use. This will run through the "dockerfile" in the repo. It will start with the python 3.8 alpine Linux image and then add in the python requirements, copy the files needs from the cloned repo and save the image in your local docker registry for use later.
```bash
sudo docker build hermes-app-time -t <image_name>
```
replace <image_name> with whatever you want to call the image.
5. Create and start the docker container
```bash
sudo docker run -it -d \
        --restart always \
        --name <container_name> \
        -e "TZ=<TZ Name>" \
        -e "MQTT_HOST=<MQTT Host/IP>" \
        -e "MQTT_PORT=<MQTT Port (Typically:1883)" \
        -e "MQTT_USER=<MQTT User>" \
        -e "MQTT_PASSWORD=<MQTT Password>" \
        <image_name>
```
Replace the following:
<container name> = Whatever you want to call the running Docker container
<TZ Name> = A valid Linux Time Zone name (example list here: https://logic.edchen.org/linux-all-available-time-zones/)
<MQTT Host/IP> = The hostname or IP address of your MQTT broker
<MQTT Port> = The port of your MQTT broker, usually 1883 but Rhasspy's internal one uses something different
<MQTT User> = The username used to connect to your MQTT broker
<MQTT Password> = The password used to connect to your MQTT broker
<image_name> = The image name defined in step 4
6. Log out of that server and login to your Rhasspy device that is doing the intent handling
7. Navigate to the profile folder
For example:
```bash
cd /profiles/en
```
Your profiles folder may be different. It is listed on the settings page on your Rhasspy device's web UI.
8. Navigate to the slot_programs folder and create a new folder for this skill and navigate into it
```bash
cd slot_programs
mkdir time
cd time
```
9. Copy the slot program down from my repo and mark it executable
```bash
wget https://raw.githubusercontent.com/MCHellspawn/hermes-app-time/master/slot_programs/timezones
chmod +x ./timezones
```
10. Open the Sentences page on your Rhasspy device (the same one you put the slot program on)
11. [Optional] Create a new sentence file (I create 1 sentence file for each skill for organization)
12. Create sentences to fire the intents
```ini
[TimeGetTime]
timezones = $time/timezones
what is the [current] time
what time is it
tell me the time
what time is it in [the] (<timezones>){timezone} [timezone]
what is the [current] time in [the] (<timezones>){timezone} [timezone]
time

[TimeTzDiff]
what is the time difference between (<TimeGetTime.timezones>){timezone1} and (<TimeGetTime.timezones>){timezone2}
```
12. Save the sentences and retrain Rhasspy.

Give it a shot. If you hasve any trouble let me know.