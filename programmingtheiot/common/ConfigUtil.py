import configparser
import logging
import os
import traceback
from pathlib import Path

from programmingtheiot.common.Singleton import Singleton
import programmingtheiot.common.ConfigConst as ConfigConst

class ConfigUtil(metaclass=Singleton):
    """
    A utility wrapper around Python's configparser.
    Implements a Singleton for consistent configuration across CDA.
    """

    configFile = ConfigConst.DEFAULT_CONFIG_FILE_NAME
    configParser = configparser.ConfigParser()
    isLoaded = False

    def __init__(self, configFile: str = None):
        if configFile:
            self.configFile = configFile
        self._loadConfig()
        logging.info(f"Created instance of ConfigUtil: {self}")

    def getConfigFileName(self) -> str:
        return self.configFile

    def getProperty(self, section: str, key: str, defaultVal: str = None, forceReload: bool = False):
        return self._getConfig(forceReload).get(section, key, fallback=defaultVal)

    def getBoolean(self, section: str, key: str, defaultVal: bool = False, forceReload: bool = False):
        return self._getConfig(forceReload).getboolean(section, key, fallback=defaultVal)

    def getInteger(self, section: str, key: str, defaultVal: int = 0, forceReload: bool = False):
        return self._getConfig(forceReload).getint(section, key, fallback=defaultVal)

    def getFloat(self, section: str, key: str, defaultVal: float = 0.0, forceReload: bool = False):
        return self._getConfig(forceReload).getfloat(section, key, fallback=defaultVal)

    def hasProperty(self, section: str, key: str) -> bool:
        return self._getConfig().has_option(section, key)

    def hasSection(self, section: str) -> bool:
        return self._getConfig().has_section(section)

    def isConfigDataLoaded(self) -> bool:
        return self.isLoaded

    def _loadConfig(self):
        pathsToTry = [self.configFile, ConfigConst.DEFAULT_CONFIG_FILE_NAME,
                      ConfigConst.PARENT_PATH + ConfigConst.DEFAULT_CONFIG_FILE_NAME]

        for path in pathsToTry:
            if self.isLoaded:
                break
            if os.path.exists(path):
                logging.info(f"Loading config file: {path}")
                self._doLoadConfig(path)
            else:
                logging.debug(f"Config file not found at: {path}")

        if not self.isLoaded:
            logging.warning("No config file loaded. System running without proper configuration.")
        else:
            logging.debug(f"Loaded config sections: {self.configParser.sections()}")

    def _doLoadConfig(self, configFilePath: str):
        try:
            self.configParser.read(configFilePath)
            self.isLoaded = True
            logging.info(f"Config file successfully loaded: {configFilePath}")
        except Exception as e:
            logging.error(f"Failed to load config file {configFilePath}: {e}")
            traceback.print_exc()

    def _getConfig(self, forceReload: bool = False) -> configparser.ConfigParser:
        if not self.isLoaded or forceReload:
            self._loadConfig()
        return self.configParser

    def getCredentials(self, section: str) -> dict:
        if self.hasSection(section):
            credFileName = self.getProperty(section, ConfigConst.CRED_FILE_KEY)
            try:
                if os.path.exists(credFileName) and os.path.isfile(credFileName):
                    logging.info(f"Loading credentials from section {section} file {credFileName}")
                    fileRef = Path(credFileName)
                    credData = f"[{ConfigConst.CRED_SECTION}]\n" + fileRef.read_text()

                    credParser = configparser.ConfigParser()
                    credParser.optionxform = str
                    credParser.read_string(credData)
                    return dict(credParser.items(ConfigConst.CRED_SECTION))
                else:
                    logging.warning(f"Credential file doesn't exist: {credFileName}")
            except Exception as e:
                logging.warning(f"Failed to load credentials from {credFileName}: {e}")
                traceback.print_exc()
        return None
