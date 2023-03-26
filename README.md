# Rhasspy Time Skill (Rhasspy_App_Time)

A skill for [Rhasspy](https://github.com/rhasspy) that provides various time related intents including the current time, the time in another timezone, and the time difference between the current timezone and another. This skill is implemented as a Hermes app and uses the [Rhasspy-hermes-app](https://github.com/rhasspy/rhasspy-hermes-app) library. The script can be run as a service, or as a docker container (recommended). 

## Installing

Requires:
* rhasspy-hermes-app 1.1.2
* pytz 2022.7
* backports.zoneinfo 0.2.1

### In Docker:
To install, clone the repository and execute docker build to build the image.

```bash
sudo docker build hermes-app-time -t <image_name>
```

### In Rhasspy:
Create a new sentence file and copy the sentences from the sentences.ini into the new file in Rhasspy and save. Retrain Rhasspy.

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