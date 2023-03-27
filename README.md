# Rhasspy Volume Satelitte Skill (Rhasspy_SatApp_Volume)

A skill for [Rhasspy](https://github.com/rhasspy) satelittes that provides various audio volume control related intents including increasing the volume, decreasing the volume, and setting the volume to a specific value. This skill is implemented as a Hermes app and uses the [Rhasspy-hermes-app](https://github.com/rhasspy/rhasspy-hermes-app) library. The script is intended to be run as a service. 

## Installing

Requires:
* rhasspy-hermes-app 1.1.2

### In Rhasspy Satellite O/S:
To install, clone the repository and execute docker build to build the image.
```bash
git clone https://github.com/MCHellspawn/hermes-satapp-volume
```

Edit the config file config/config.ini
1. In the Alsa Setup section set the device name to control (I want to pull this from the Rhasspy config in the future)
2. In the Rhasspy section set the hostname/ip and port of you base device (This is the device where the intent recognition is configured, this is used for auto installing a sentences file)
3. In the Rhasspy section set the setellite id of device the skill is being run on (This is used for generating intent names)

```bash
cd hermes-satapp-volume
chmod +x ./setup-service-volume.sh
sudo ./setup-service-volume.sh
```

### In Rhasspy:
 a new sentence file and copy the sentences from the sentences.ini into the new file in Rhasspy and save. Retrain Rhasspy.

Setup the slot program:
1. SSH into the Rhasspy device 
   * If using a base/satellite setup this is typically done on the base
2. Navigate to your slot programs folder
   * for example "/profiles/en/slot_programs"
```bash
cd /profiles/en/slot_programs
```
3. Create a folder name "time" and navigate to it
```bash
mkdir time
cd time
```
4. Download the slot program from the github repo
```bash
wget https://raw.githubusercontent.com/MCHellspawn/hermes-app-time/master/slot_programs/timezones
```
5. Setup the slot variables
```ini
timezones = $time/timezones
```
6. Use the slot variable in a sentence
```ini
what time is it in [the] (<timezones>){timezone} [timezone]
```

## Configuration

The TZ environment variable needs to be set to the a valid linux timezone value when creating the docker container.

It is not necessary but you may also edit the config/responses.txt file to add or remove some of the available responses for an intent.

## Using

Build a docker container using the image created above.

Bind the config volume <path/on/host>:/app/config

```bash
sudo docker run -it -d \
        --restart always \
        --name <container_name> \
        -e "TZ=America/New_York" \
        -e "MQTT_HOST=<MQTT Host/IP>" \
        -e "MQTT_PORT=<MQTT Port (Typically:1883)" \
        -e "MQTT_USER=<MQTT User>" \
        -e "MQTT_PASSWORD=<MQTT Password>" \
        <image_name>
```

The following intents are implemented on the hermes MQTT topic:

```ini
[TimeGetTime]

[TimeTzDiff]
```

## To-Do

* Clean up install process
* More intents
  * Time stuff <any ideas?>