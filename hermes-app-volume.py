"""Skill to tell you the time."""
import asyncio
import logging
import random
import aiohttp
import configparser
import json
from sys import platform
from skill import IntentNames, RhasspySkill, SessionCustomData
from rhasspyclient import RhasspyClient
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession, HermesApp

_APPNAME = "VolumeApp"
_LOGGER = logging.getLogger(_APPNAME)

app = HermesApp(_APPNAME)
skill = None

# currently not used, replaced by setup_skill method in skill class
async def setup_skill():
    global _LOGGER
    
    data = {}
    sentencesString = ""

    async with aiohttp.ClientSession(headers=[("Content-Type", "application/json")]) as session:
        client = RhasspyClient("http://192.168.1.90:12101/api", session)
        rhasspyConfig = await client.get_profile()
    
    if rhasspyConfig["intent"]['system'] == "hermes":
        intentHandlerUrl = rhasspyConfig["mqtt"]["host"]
    if rhasspyConfig["intent"]['system'] == "remote":        
        intentHandlerUrl = rhasspyConfig["intent"]["remote"]["url"][7:rhasspyConfig["intent"]["remote"]["url"].find(":12101/")]
    
    # open the sentence file in read mode and split into a list
    sentences = configparser.ConfigParser(allow_no_value=True)
    sentences.read("./sentences.ini")

    _LOGGER.info(f"Setup: Sentences file read")

    for section in sentences.sections():
        sentencesString = f"{sentencesString}[{section}]\n"
        for key in sentences[section]: 
            sentencesString = f"{sentencesString}{key}\n"
        sentencesString = f"{sentencesString}\n"   
    
    data["intents/volume.ini"] = sentencesString

    _LOGGER.info(f"Setup: Sentences POST data built")
    
    async with aiohttp.ClientSession(headers=[("Content-Type", "application/json")]) as session:
        async with session.post(
                "http://192.168.1.90:12101/api/sentences", data=json.dumps(data)
            ) as response:
                response.raise_for_status()
                result = await response.text()
                _LOGGER.info(f"Setup: Sentences POST result: {result}")
        #client = RhasspyClient("http://192.168.1.90:12101/api", session)
        #result = await client.train(no_cache=True)
        _LOGGER.info(f"Setup: Train POST result: {result}")

def response_sentence(intent: NluIntent, data_string: str):
    _LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

    # open the responses file in read mode
    responses = configparser.ConfigParser(allow_no_value=True)
    responses.read("config/responses.ini")
    
    baseIntentName = intent.intent.intent_name.replace(intent.site_id, '')
      
    sentence = random.choice(responses[baseIntentName]).format(data_string)

    _LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
    _LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
    return sentence

def fail_sentence(intent: NluIntent, errName: str):
    _LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

    # open the responses file in read mode
    responses = configparser.ConfigParser(allow_no_value=True)
    responses.read("config/responses.ini")
    
    intentErrName = f"{intent.intent.intent_name.replace(intent.site_id, '')}-Fail-{errName}"
      
    sentence = random.choice(responses[intentErrName])

    _LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
    _LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
    return sentence

def get_master_volume():
    vol = None
    
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        vol = get_master_volume_linux()
    elif platform == "win32":
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        vol = volume.GetMasterVolumeLevel()
    return vol

def get_master_volume_linux():
    proc = subprocess.Popen('/usr/bin/amixer', shell=True, stdout=subprocess.PIPE, encoding='utf8')
    amixer_stdout = proc.communicate()[0].split('\n')[4]
    proc.wait()
    find_start = amixer_stdout.find('[') + 1
    find_end = amixer_stdout.find('%]', find_start)
    return float(amixer_stdout[find_start:find_end])

def set_master_volume(volume):
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        vol = set_master_volume_linux(volume)
    elif platform == "win32":
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        interfaceVolume = cast(interface, POINTER(IAudioEndpointVolume))
        interfaceVolume.volume.SetMasterVolumeLevel(-37, None)

def set_master_volume_linux(volume):
    proc = subprocess.Popen('/usr/bin/amixer', shell=True, stdout=subprocess.PIPE, encoding='utf8')
    amixer_stdout = proc.communicate()[0].split('\n')[0]
    proc.wait()
    find_start = amixer_stdout.find('[') + 1
    find_end = amixer_stdout.find('%]', find_start)
    device_name = amixer_stdout[find_start:find_end]
    val = float(int(volume))
    proc = subprocess.Popen('/usr/bin/amixer sset ' + device_name + ' ' + str(val) + '%', shell=True, stdout=subprocess.PIPE)
    proc.wait()

@app.on_intent(IntentNames.VOLUP + '-' + skill.satellite_id)
async def vol_up(intent: NluIntent):
    """Turn the volume up."""
    _LOGGER.info(f"Intent: {intent.id} | Started: {IntentNames.VOLUP}")
    
    sentence = None
      
    _LOGGER.info(f"Intent: {intent.id} | Responded to {IntentNames.VOLUP}")
    _LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
    _LOGGER.info(f"Intent: {intent.id} | Completed: {IntentNames.VOLUP}")
    return EndSession(sentence)

@app.on_intent(IntentNames.VOLDOWN + '-' + skill.satellite_id)
async def vol_down(intent: NluIntent):
    """Turn the volume up."""
    _LOGGER.info(f"Intent: {intent.id} | Started: {IntentNames.VOLDOWN}")
    
    sentence = None
      
    _LOGGER.info(f"Intent: {intent.id} | Responded to {IntentNames.VOLDOWN}")
    _LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
    _LOGGER.info(f"Intent: {intent.id} | Completed: {IntentNames.VOLDOWN}")
    return EndSession(sentence)

@app.on_intent(IntentNames.VOLSET + '-' + skill.satellite_id)
async def vol_set(intent: NluIntent):
    """Set the volume."""
    _LOGGER.info(f"Intent: {intent.id} | Started: {IntentNames.VOLSET}")
    
    sentence = None
    
    volumeslot = next((slot for slot in intent.slots if slot.slot_name == 'volumesetting'), None)
    if volumeslot == None:
        sentence = fail_sentence(intent, "NoSlotVolume")
    else:
        set_master_volume(volumeslot.value['value'])
        sentence = response_sentence(intent, volumeslot.value['value'])
      
    _LOGGER.info(f"Intent: {intent.id} | Responded to {IntentNames.VOLSET}")
    _LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
    _LOGGER.info(f"Intent: {intent.id} | Completed: {IntentNames.VOLSET}")
    return EndSession(sentence)

@app.on_intent(IntentNames.VOLGET + '-' + skill.satellite_id)
async def vol_get(intent: NluIntent):
    """Turn the volume up."""
    _LOGGER.info(f"Intent: {intent.id} | Started: {IntentNames.VOLGET}")
    
    vol = get_master_volume()
       
    sentence = response_sentence(intent, str(vol))
      
    _LOGGER.info(f"Intent: {intent.id} | Responded to {IntentNames.VOLGET}")
    _LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
    _LOGGER.info(f"Intent: {intent.id} | Completed: {IntentNames.VOLGET}")
    return EndSession(sentence)

if __name__ == "__main__":
    _LOGGER.info(f"Starting Hermes Satelitte App: {_APPNAME}")
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        import subprocess
        _LOGGER.info("Satelitte App: Imports loaded (linux)")
    elif platform == "win32":
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            _LOGGER.info(f"Satelitte App {_APPNAME}: Imports loaded (windows)")
        except ImportError:
            _LOGGER.error(f"Satelitte App {_APPNAME}: Imports failed to load (windows)")

    skill = RhasspySkill(_APPNAME)
    _LOGGER.info(f"Setup Completed Satelitte App: {_APPNAME}")
    app.run()