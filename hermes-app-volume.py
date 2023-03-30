"""Skill to control the volume."""
import logging
from skill import RhasspySkill
from rhasspyhermes_app import HermesApp

_APPNAME = "VolumeApp"
_LOGGER = logging.getLogger(_APPNAME)

if __name__ == "__main__":
    _LOGGER.info(f"Starting Hermes Satelitte App: {_APPNAME}")
    app = HermesApp(_APPNAME)
    _LOGGER.info(f"Setup starting Satelitte App: {_APPNAME}")
    skill = RhasspySkill(name = _APPNAME, app = app, logger = _LOGGER)
    _LOGGER.info(f"Setup Completed Satelitte App: {_APPNAME}")
    _LOGGER.info(f"Running Satelitte App: {_APPNAME}")
    app.run()