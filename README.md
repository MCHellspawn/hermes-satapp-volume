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

The following intents are implemented on the hermes MQTT topic:

```ini
[VolumeVolumeUp]

[VolumeVolumeDown]

[VolumeVolumeSet]

[VolumeVolumeGet]
```

## To-Do

* Make it work from sat device