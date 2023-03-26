import asyncio
import os
import io
import aiohttp
import configparser
import json
from enum import Enum
from typing import Optional
from rhasspyclient import RhasspyClient
from pydantic import BaseModel

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
    name = None
    config = None
    _LOGGER = None
    apiUrl = None
    satellite_id = None
    
    def __init__(self, name, config = None, logger = None) -> None:
        self.name = name
        if config == None:
            config = self.read_configuration_file()
        self.config = config
        self.apiUrl = f"{self.config['Rhasspy']['protocol']}://{self.config['Rhasspy']['host']}:{self.config['Rhasspy']['port']}/api"
        self.satellite_id = self.config['Rhasspy']['satellite_id']
        if logger != None:
            self._LOGGER = logger            
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.setup_skill())    
    
    async def setup_skill(self):
        
        data = {}
        sentencesString = ""

        # open the sentence file in read mode and split into a list
        sentences = configparser.ConfigParser(allow_no_value=True)
        sentences.read("./sentences.ini")

        if self._LOGGER != None:
            self._LOGGER.info(f"Setup: Sentences file read")

        for section in sentences.sections():
            sentencesString = f"{sentencesString}[{section}]\n"
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
                    self._LOGGER.info(f"Setup: Sentences POST result: {result}")
            client = RhasspyClient(f"{self.apiUrl}/api", session)
            result = await client.train(no_cache=True)
            self._LOGGER.info(f"Setup: Train POST result: {result}")

    def read_configuration_file(self):
        try:
            cp = configparser.ConfigParser()
            with io.open(os.path.dirname(__file__) + "/config/config.ini", encoding="utf-8") as f:
                cp.read_file(f)
            return {section: {option_name: option for option_name, option in cp.items(section)}
                    for section in cp.sections()}
        except (IOError, configparser.Error):
            return dict()
