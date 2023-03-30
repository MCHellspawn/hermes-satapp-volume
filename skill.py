import asyncio
import os
import io
import aiohttp
import configparser
import json
import random
from enum import Enum
from sys import platform
from typing import Optional
from pydantic import BaseModel
from rhasspyclient import RhasspyClient
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession, HermesApp

if platform == "linux" or platform == "linux2" or platform == "darwin":
    import subprocess
elif platform == "win32":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class SessionCustomData(BaseModel):
    intent_name: str
    input_text: str
    intent_slots: Optional[str]

class IntentNames(str, Enum):
    VOLUP = f"VolumeVolumeUp"
    VOLDOWN = f"VolumeVolumeDown"
    VOLSET = f"VolumeVolumeSet"
    VOLGET = f"VolumeVolumeGet"
    TOGGLEMUTE = f"VolumeToggleMute"

class RhasspySkill:
    name:str = None
    app: HermesApp = None
    config = None
    _LOGGER = None
    apiUrl = None
    satellite_id = None
    intents = None
        
    def __init__(self, name: str, app: HermesApp, config = None, logger = None) -> None:
        self.name = name
        self.app = app
        if config == None:
            config = self.read_configuration_file()
        self.config = config
        self.apiUrl = f"{self.config['Rhasspy']['protocol']}://{self.config['Rhasspy']['host']}:{self.config['Rhasspy']['port']}/api"
        self.satellite_id = self.config['Rhasspy']['satellite_id']
        if logger != None:
            self._LOGGER = logger
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.setup_skill_on_rhasspy())

    async def setup_skill_on_rhasspy(self):
        data = {}
        sentencesString = ""

        # Sentence setup
        async with aiohttp.ClientSession(headers=[("accept", "application/json")]) as session:
            async with session.get(
                f"{self.apiUrl}/sentences"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                self._LOGGER.debug(f"Setup: Sentences GET result: {result}")
                if result.get(f"intents/volume-{self.satellite_id}.ini") == None:
                    self._LOGGER.info(f"Setup: Sentences file note found")
                    # open the sentence file in read mode and split into a list
                    sentences = configparser.ConfigParser(allow_no_value=True)
                    sentences.read("./sentences.ini")

                    if self._LOGGER != None:
                        self._LOGGER.info(f"Setup: Sentences config file read")

                        # parse sentences config file
                        for section in sentences.sections():
                            sentencesString = f"{sentencesString}[{section}-{self.satellite_id}]\n"
                            for key in sentences[section]: 
                                sentencesString = f"{sentencesString}{key}\n"
                            sentencesString = f"{sentencesString}\n"   
                        
                        data[f"intents/volume-{self.satellite_id}.ini"] = sentencesString

                        if self._LOGGER != None:
                            self._LOGGER.info(f"Setup: Sentences POST data built")
                        
                        async with aiohttp.ClientSession(headers=[("Content-Type", "application/json")]) as session:
                            async with session.post(
                                    f"{self.apiUrl}/sentences", data=json.dumps(data)
                                ) as response:
                                    response.raise_for_status()
                                    result = await response.text()
                                    self._LOGGER.debug(f"Setup: Sentences POST result: {result}")
                            client = RhasspyClient(f"{self.apiUrl}", session)
                            result = await client.train(no_cache=True)
                            self._LOGGER.info(f"Setup: Train POST result: {result}")
                    else:
                        self._LOGGER.info(f"Setup: Sentences config file not read")
                else:
                    self._LOGGER.info(f"Setup: Sentences file exists")

        # Register intent handlers
        self.app.on_intent(IntentNames.VOLGET + '-' + self.satellite_id)(self.vol_get)
        self.app.on_intent(IntentNames.VOLUP + '-' + self.satellite_id)(self.vol_up)
        self.app.on_intent(IntentNames.VOLDOWN + '-' + self.satellite_id)(self.vol_down)
        self.app.on_intent(IntentNames.VOLSET + '-' + self.satellite_id)(self.vol_set)

    def read_configuration_file(self):
        try:
            cp = configparser.ConfigParser()
            with io.open(os.path.dirname(__file__) + "/config/config.ini", encoding="utf-8") as f:
                cp.read_file(f)
            return {section: {option_name: option for option_name, option in cp.items(section)}
                    for section in cp.sections()}
        except (IOError, configparser.Error):
            return dict()

    def response_sentence(self, intent: NluIntent, data_string: str):
        self._LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

        # open the responses file in read mode
        responses = configparser.ConfigParser(allow_no_value=True)
        responses.read("config/responses.ini")
        
        baseIntentName = intent.intent.intent_name.replace(f"-{intent.site_id}", '')
        
        intentResponses = responses.items(baseIntentName)[0]
        
        sentence = random.choice(intentResponses[0:-1]).format(data_string)

        self._LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
        self._LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
        return sentence

    def fail_sentence(self, intent: NluIntent, errName: str):
        self._LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

        # open the responses file in read mode
        responses = configparser.ConfigParser(allow_no_value=True)
        responses.read("config/responses.ini")
        
        intentErrName = f"{intent.intent.intent_name.replace(f'-{intent.site_id}', '')}-Fail-{errName}"

        intentErrResponses = responses.items(intentErrName)[0]
        
        sentence = random.choice(intentErrResponses[0:-1])

        self._LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
        self._LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
        return sentence

    def get_master_volume(self):
        vol = None
        
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            vol = self.get_master_volume_linux()
        elif platform == "win32":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            vol_range = volume.GetVolumeRange()
            rawvol = volume.GetMasterVolumeLevel()
            vol = int(round((rawvol - (vol_range[0])) / (vol_range[1] - (vol_range[0])) * 100, 0))
        return vol

    def get_master_volume_linux(self):
        proc = subprocess.Popen('/usr/bin/amixer', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        amixer_stdout = proc.communicate()[0].split('\n')[4]
        proc.wait()
        find_start = amixer_stdout.find('[') + 1
        find_end = amixer_stdout.find('%]', find_start)
        return float(amixer_stdout[find_start:find_end])

    async def vol_get(self, intent: NluIntent):
        """Get the volume level."""
        self._LOGGER.info(f"Intent: {intent.id} | Started: vol_get")
        
        vol = self.get_master_volume()
        self._LOGGER.info(f"Intent: {intent.id} | volume retrieved {vol}")
        
        sentence = self.response_sentence(intent, str(vol))
        self._LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
        
        self.app.notify(sentence, intent.site_id)
        self._LOGGER.info(f"Intent: {intent.id} | Responded to vol_get")
        self._LOGGER.info(f"Intent: {intent.id} | Completed: vol_get")
        return EndSession()

    async def vol_up(self, intent: NluIntent):
        """Turn the volume up."""
        self._LOGGER.info(f"Intent: {intent.id} | Started: vol_up")
        
        sentence = None
        
        self._LOGGER.info(f"Intent: {intent.id} | Responded to vol_up")
        self._LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
        self._LOGGER.info(f"Intent: {intent.id} | Completed: vol_up")
        return EndSession(sentence)

    async def vol_down(self, intent: NluIntent):
        """Turn the volume up."""
        self._LOGGER.info(f"Intent: {intent.id} | Started: vol_down")
        
        sentence = None
        
        self._LOGGER.info(f"Intent: {intent.id} | Responded to vol_down")
        self._LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
        self._LOGGER.info(f"Intent: {intent.id} | Completed: vol_down")
        return EndSession(sentence)

    async def vol_set(self, intent: NluIntent):
        """Set the volume."""
        self._LOGGER.info(f"Intent: {intent.id} | Started: vol_set")
        
        sentence = None
        
        volumeslot = next((slot for slot in intent.slots if slot.slot_name == 'volumesetting'), None)
        if volumeslot == None:
            sentence = self.fail_sentence(intent, "NoSlotVolume")
        else:
            self.set_master_volume(volumeslot.value['value'])
            sentence = self.response_sentence(intent, volumeslot.value['value'])
        
        self._LOGGER.info(f"Intent: {intent.id} | Responded to vol_set")
        self._LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")
        self._LOGGER.info(f"Intent: {intent.id} | Completed: vol_set")
        return EndSession(sentence)
