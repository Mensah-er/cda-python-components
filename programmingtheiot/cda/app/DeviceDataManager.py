import logging
from time import sleep

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
    DeviceDataManager class updated for PIOT-CDA-10-004.
    Adds MQTT, CoAP integration, actuator callback handling,
    and upstream transmission for sensor and system performance data.
    """

    def __init__(self, disableAllComms: bool = False):
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

        # Communication connectors
        self.mqttClient = None
        self.coapClient = None
        self.coapServer = None

        # Caches
        self.actuatorResponseCache = {}
        self.sensorDataCache = {}
        self.systemPerfDataCache = {}

        # --- System, Sensor, and Actuator Managers ---
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

        # --- Device-specific settings ---
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

        # --- Enable MQTT Client ---
        self.enableMqttClient = self.configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.ENABLE_MQTT_CLIENT_KEY
        )

        # Apply disableAllComms for testing
        if disableAllComms:
            self.enableMqttClient = False
            self.coapClient = None
            self.coapServer = None
            logging.info("All communications disabled for testing")

        if self.enableMqttClient:
            logging.info("MQTT Client enabled. Initializing MqttClientConnector...")
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)
        else:
            logging.info("MQTT Client disabled in configuration.")

    # --------------------------------------------------------------------------
    # Public interface methods
    # --------------------------------------------------------------------------
    def startManager(self):
        logging.info("Starting DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.startManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.startManager()

        # Start MQTT client
        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)

        logging.info("DeviceDataManager started successfully.")

    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.stopManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.stopManager()

        # Stop MQTT client
        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()

        logging.info("DeviceDataManager stopped successfully.")

    # --------------------------------------------------------------------------
    # IDataMessageListener callback methods
    # --------------------------------------------------------------------------
    def handleActuatorCommandMessage(self, data: ActuatorData = None) -> ActuatorData:
        logging.info("Processing actuator command message: " + str(data))

        if data:
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
            self._handleUpstreamTransmission(resourceName=resourceName, msg=actuatorMsg)
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

            # Analyze sensor data
            self._handleSensorDataAnalysis(data)

            # Convert to JSON and send upstream
            jsonData = DataUtil().sensorDataToJson(data)
            self._handleUpstreamTransmission(
                resourceName=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE,
                msg=jsonData
            )

            return True
        else:
            logging.warning("Incoming sensor data is invalid (null). Ignoring.")
            return False

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData = None) -> bool:
        if data:
            logging.debug("Incoming system performance data received: " + str(data))

            # Convert to JSON and send upstream
            jsonData = DataUtil().systemPerformanceDataToJson(data)
            self._handleUpstreamTransmission(
                resourceName=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                msg=jsonData
            )

            return True
        else:
            logging.warning("Incoming system performance data is invalid (null). Ignoring.")
            return False

    # --------------------------------------------------------------------------
    # Private helper methods
    # --------------------------------------------------------------------------
    def _handleIncomingDataAnalysis(self, msg: str):
        logging.debug("Analyzing incoming data: " + str(msg))
        # Placeholder for data analysis

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

        # Send message via MQTT if enabled
        if self.mqttClient:
            if self.mqttClient.publishMessage(resourceName, msg, qos=ConfigConst.DEFAULT_QOS):
                logging.debug(f"Published incoming data to resource (MQTT): {resourceName}")
            else:
                logging.warning(f"Failed to publish incoming data to resource (MQTT): {resourceName}")

        # Send message via CoAP if enabled
        if self.coapClient:
            if self.coapClient.sendPutRequest(resourceName, msg):
                logging.debug(f"Put incoming message data to resource (CoAP): {resourceName}")
            else:
                logging.warning(f"Failed to put incoming message data to resource (CoAP): {resourceName}")

    # --------------------------------------------------------------------------
    # Cache retrieval methods
    # --------------------------------------------------------------------------
    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        return self.actuatorResponseCache.get(name, None)

    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        return self.sensorDataCache.get(name, None)

    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        return self.systemPerfDataCache.get(name, None)

    # --------------------------------------------------------------------------
    # Listener setters
    # --------------------------------------------------------------------------
    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        pass

    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        pass
