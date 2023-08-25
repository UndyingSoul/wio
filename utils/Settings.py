import json
import logging
import os

class Setting():
    def __init__(self):
        settingsFileLocation = "./config/settings.json"
        settingsDictionary = {}
        LOGGING_LEVEL_MAPPER = {
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "WARN": logging.WARNING,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if os.path.exists(settingsFileLocation):
            with open(settingsFileLocation, "r") as f:
                settingsDictionary = json.load(f)
                
        self._loggingLevel = LOGGING_LEVEL_MAPPER[settingsDictionary["loggingLevel"]
                                                  ] if "loggingLevel" in settingsDictionary.keys() else logging.INFO
        self._logToFile = settingsDictionary["logToFile"] if "logToFile" in settingsDictionary.keys(
        ) else True

    def alwaysTrue():
        return True

    @property
    def loggingLevel(self):
        return int(self._loggingLevel)

    @property
    def logToFile(self):
        return self._logToFile
