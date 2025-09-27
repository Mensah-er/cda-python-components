#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 

import random
import logging

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataSet

class BaseSensorSimTask:
    """
    Base class for sensor simulation tasks.
    Handles both random and dataset-driven telemetry generation.
    """

    DEFAULT_MIN_VAL = ConfigConst.DEFAULT_VAL
    DEFAULT_MAX_VAL = 100.0

    def __init__(self, 
                 name: str = ConfigConst.NOT_SET, 
                 typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, 
                 dataSet: SensorDataSet = None, 
                 minVal: float = DEFAULT_MIN_VAL, 
                 maxVal: float = DEFAULT_MAX_VAL):
        self.name = name
        self.typeID = typeID
        self.dataSet = dataSet
        self.dataSetIndex = 0
        self.useRandomizer = False
        self.latestSensorData = None

        if not self.dataSet:
            self.useRandomizer = True
            self.minVal = minVal
            self.maxVal = maxVal

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(typeID=self.getTypeID(), name=self.getName())
        sensorVal = ConfigConst.DEFAULT_VAL

        if self.useRandomizer:
            sensorVal = random.uniform(self.minVal, self.maxVal)
        else:
            sensorVal = self.dataSet.getDataEntry(index=self.dataSetIndex)
            self.dataSetIndex += 1

            # Wrap-around if we reach the end of the dataset
            if self.dataSetIndex >= self.dataSet.getDataEntryCount():
                self.dataSetIndex = 0

        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData

        return self.latestSensorData

    def getTelemetryValue(self) -> float:
        if not self.latestSensorData:
            self.generateTelemetry()
        return self.latestSensorData.getValue()

    def getLatestTelemetry(self) -> SensorData:
        return self.latestSensorData

    def getName(self) -> str:
        return self.name

    def getTypeID(self) -> int:
        return self.typeID
