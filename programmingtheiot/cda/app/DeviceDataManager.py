import logging

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil


class DeviceDataManager(IDataMessageListener):
    """
    Implementation of the DeviceDataManager class as per professor instructions.
    Handles system performance, sensor, and actuator messages for CDA.
    """

    def __init__(self):
        self.configUtil = ConfigUtil()

        self.enableSystemPerf = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SYSTEM_PERF_KEY
        )

        self.enableSensing = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SENSING_KEY
        )

        self.enableActuation = True

        self.sysPerfMgr = None
        self.sensorAdapterMgr = None
        self.actuatorAdapterMgr = None

        # Optional, for later communication
        self.mqttClient = None
        self.coapClient = None
        self.coapServer = None

        # Caches for responses
        self.actuatorResponseCache = {}
        self.sensorDataCache = {}
        self.systemPerfDataCache = {}

        if self.enableSystemPerf:
            self.sysPerfMgr = SystemPerformanceManager()
            self.sysPerfMgr.setDataMessageListener(self)
            logging.info("Local system performance tracking enabled")

        if self.enableSensing:
            self.sensorAdapterMgr = SensorAdapterManager()
            self.sensorAdapterMgr.setDataMessageListener(self)
            logging.info("Local sensor tracking enabled")

        if self.enableActuation:
            self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener=self)
            logging.info("Local actuation capabilities enabled")

        self.handleTempChangeOnDevice = self.configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY
        )

        self.triggerHvacTempFloor = self.configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY
        )

        self.triggerHvacTempCeiling = self.configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY
        )

    # -------------------------
    # Public interface methods
    # -------------------------
    def startManager(self):
        logging.info("Starting DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.startManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.startManager()

        logging.info("Started DeviceDataManager.")

    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.stopManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.stopManager()

        logging.info("Stopped DeviceDataManager.")

    # IDataMessageListener callback methods
    def handleActuatorCommandMessage(self, data: ActuatorData = None) -> ActuatorData:
        logging.info("Actuator data: " + str(data))

        if data:
            logging.info("Processing actuator command message.")
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        else:
            logging.warning("Incoming actuator command is invalid (null). Ignoring.")
            return None

    def handleActuatorCommandResponse(self, data: ActuatorData = None) -> bool:
        if data:
            logging.debug("Incoming actuator response received: " + str(data))
            self.actuatorResponseCache[data.getName()] = data

            actuatorMsg = DataUtil().actuatorDataToJson(data)
            resourceName = ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE
            self._handleUpstreamTransmission(resource=resourceName, msg=actuatorMsg)
            return True
        else:
            logging.warning("Incoming actuator response is invalid (null). Ignoring.")
            return False

    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        logging.debug(f"handleIncomingMessage called with resource: {resourceEnum}, msg: {msg}")
        self._handleIncomingDataAnalysis(msg)
        return True

    def handleSensorMessage(self, data: SensorData = None) -> bool:
        if data:
            logging.debug("Incoming sensor data received: " + str(data))
            self._handleSensorDataAnalysis(data)
            return True
        else:
            logging.warning("Incoming sensor data is invalid (null). Ignoring.")
            return False

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData = None) -> bool:
        if data:
            logging.debug("Incoming system performance data received: " + str(data))
            return True
        else:
            logging.warning("Incoming system performance data is invalid (null). Ignoring.")
            return False

    # -------------------------
    # Private helper methods
    # -------------------------
    def _handleIncomingDataAnalysis(self, msg: str):
        logging.debug("Analyzing incoming data: " + str(msg))
        # For now, placeholder implementation

    def _handleSensorDataAnalysis(self, data: SensorData = None):
        if self.handleTempChangeOnDevice and data and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
            logging.info("Handling temp change: %s, typeID: %s", str(self.handleTempChangeOnDevice), str(data.getTypeID()))

            ad = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)

            if data.getValue() > self.triggerHvacTempCeiling:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempCeiling)
            elif data.getValue() < self.triggerHvacTempFloor:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempFloor)
            else:
                ad.setCommand(ConfigConst.COMMAND_OFF)

            self.handleActuatorCommandMessage(ad)

    def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
        logging.debug(f"Upstream transmission called for resource {resourceName}: {msg}")
        # Placeholder for MQTT/CoAP sending

    # -------------------------
    # Cache retrieval methods
    # -------------------------
    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        return self.actuatorResponseCache.get(name, None)

    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        return self.sensorDataCache.get(name, None)

    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        return self.systemPerfDataCache.get(name, None)

    # -------------------------
    # Listener setters (optional)
    # -------------------------
    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        pass

    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        pass
