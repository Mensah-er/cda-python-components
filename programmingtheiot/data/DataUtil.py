#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License.
#
#####

import json
import logging
from decimal import Decimal
from json import JSONEncoder

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DataUtil():
    """
    Utility class for converting IoT data objects to and from JSON.
    """

    def __init__(self, encodeToUtf8: bool = False):
        self.encodeToUtf8 = encodeToUtf8
        logging.info("Created DataUtil instance.")

    # ----------------------------------------------------------------------
    # JSON Conversion: Object -> JSON String
    # ----------------------------------------------------------------------
    def actuatorDataToJson(self, data: ActuatorData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("ActuatorData is null. Returning empty string.")
            return ""
        return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

    def sensorDataToJson(self, data: SensorData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("SensorData is null. Returning empty string.")
            return ""
        return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

    def systemPerformanceDataToJson(self, data: SystemPerformanceData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("SystemPerformanceData is null. Returning empty string.")
            return ""
        return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

    # ----------------------------------------------------------------------
    # JSON Conversion: JSON String -> Object
    # ----------------------------------------------------------------------
    def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat)
        ad = ActuatorData()
        self._updateIotData(jsonStruct, ad)
        return ad

    def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat)
        sd = SensorData()
        self._updateIotData(jsonStruct, sd)
        return sd

    def jsonToSystemPerformanceData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat)
        spd = SystemPerformanceData()
        self._updateIotData(jsonStruct, spd)
        return spd

    # ----------------------------------------------------------------------
    # Private Helper Methods
    # ----------------------------------------------------------------------
    def _formatDataAndLoadDictionary(self, jsonData: str, useDecForFloat: bool = False) -> dict:
        """
        Cleans and loads JSON string into a dictionary.
        """
        jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')

        if useDecForFloat:
            jsonStruct = json.loads(jsonData, parse_float=Decimal)
        else:
            jsonStruct = json.loads(jsonData)

        return jsonStruct

    def _generateJsonData(self, obj, useDecForFloat: bool = False) -> str:
        """
        Converts an object into a JSON string using JsonDataEncoder.
        """
        if self.encodeToUtf8:
            jsonData = json.dumps(obj, cls=JsonDataEncoder).encode('utf8')
        else:
            jsonData = json.dumps(obj, cls=JsonDataEncoder, indent=4)

        if jsonData:
            jsonData = str(jsonData).replace("\'", "\"").replace('False', 'false').replace('True', 'true')

        return jsonData

    def _updateIotData(self, jsonStruct: dict, obj):
        """
        Updates the attributes of the IoT data object using dictionary values.
        """
        varStruct = vars(obj)
        for key in jsonStruct:
            if key in varStruct:
                setattr(obj, key, jsonStruct[key])
            else:
                logging.warning("JSON data contains unmapped key: %s", key)


class JsonDataEncoder(JSONEncoder):
    """
    Convenience class to facilitate JSON encoding of an object that can be converted to a dict.
    """
    def default(self, o):
        return o.__dict__
