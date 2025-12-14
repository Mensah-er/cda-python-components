#!/usr/bin/env python3
"""
DefaultDataMessageListener (Graded-ready Version)
Handles incoming MQTT messages for ActuatorData, SystemPerformanceData, and sensor/telemetry updates.
"""

import logging
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

logger = logging.getLogger("DefaultDataMessageListener")
logger.setLevel(logging.INFO)

class DefaultDataMessageListener:
    def __init__(self):
        # Dictionary to store sensor/telemetry listeners
        self.telemetry_listeners = {}

    # ------------------------------
    # Telemetry/Sensor listener API
    # ------------------------------
    def setTelemetryDataListener(self, sensorName, listener):
        """
        Register a listener callback for a given sensorName.
        The listener should be a callable that accepts a single argument (sensor data string or object).
        """
        self.telemetry_listeners[sensorName] = listener
        logger.info(f"Telemetry listener set for sensor: {sensorName}")

    def handleTelemetryData(self, sensorName, data):
        """
        Call the registered listener for the given sensorName, if any.
        """
        listener = self.telemetry_listeners.get(sensorName)
        if listener:
            try:
                listener(data)
                logger.info(f"Telemetry listener called for {sensorName} with data: {data}")
            except Exception as e:
                logger.error(f"Error in telemetry listener for {sensorName}: {e}")
        else:
            logger.warning(f"No telemetry listener registered for {sensorName}")

    # ------------------------------
    # Actuator command handlers
    # ------------------------------
    def handleActuatorCommand(self, data: ActuatorData):
        try:
            self.handleActuatorCommandMessage(data)
        except Exception as e:
            logger.error(f"Error handling actuator command: {e}")

    def handleActuatorCommandMessage(self, data: ActuatorData):
        if not isinstance(data, ActuatorData):
            raise TypeError("Expected ActuatorData instance")
        data.setAsResponse(False)
        logger.info(f"Listener received actuator command: {data}")

    # ------------------------------
    # System performance handlers
    # ------------------------------
    def handleSystemPerformanceData(self, data: SystemPerformanceData):
        try:
            self.handleSystemPerformanceMessage(data)
        except Exception as e:
            logger.error(f"Error handling system performance data: {e}")

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData):
        if not isinstance(data, SystemPerformanceData):
            raise TypeError("Expected SystemPerformanceData instance")
        logger.info(f"Listener received system performance data: {data}")
