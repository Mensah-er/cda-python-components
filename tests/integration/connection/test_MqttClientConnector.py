# /piot-python-components/tests/integration/connection/test_MqttClientConnector.py

import unittest
import logging
from time import sleep
import json

from programmingtheiot.common.ConfigConst import *
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.IDataMessageListener import IDataMessageListener


class DefaultDataMessageListener(IDataMessageListener):
    """
    Simple listener for testing actuator command callback.
    Records messages received from multiple topics.
    """
    def __init__(self):
        self.listenerCalled = False
        self.receivedData = None
        self.receivedTopic = None

    def handleActuatorCommandMessage(self, data: ActuatorData):
        logging.info(f"Listener received actuator command: {data}")
        self.listenerCalled = True
        self.receivedData = data


class TestMqttClientConnector(unittest.TestCase):
    """
    Integration tests for MqttClientConnector, covering CDA and GDA topics.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO)
        cls.cfg = ConfigUtil()

    def setUp(self):
        self.mcc = MqttClientConnector(clientID="TestMqttClient")
        self.listener = DefaultDataMessageListener()
        self.mcc.setDataMessageListener(self.listener)

    def tearDown(self):
        if self.mcc:
            self.mcc.disconnectClient()

    def test_connect_disconnect(self):
        self.assertTrue(self.mcc.connectClient(), "Failed to connect to MQTT broker")
        sleep(1)
        self.assertTrue(self.mcc.disconnectClient(), "Failed to disconnect from MQTT broker")

    def test_publish_message_cda_gda(self):
        """
        Test publishing messages to all CDA and GDA actuator command topics.
        """
        self.assertTrue(self.mcc.connectClient())
        sleep(1)

        actuatorData = ActuatorData()
        payload = DataUtil().actuatorDataToJson(actuatorData)

        topics = [
            ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            ResourceNameEnum.GDA_ACTUATOR_CMD_RESOURCE
        ]

        for topic in topics:
            result = self.mcc.publishMessage(topic, payload, qos=0)
            self.assertTrue(result, f"Failed to publish to {topic}")

        sleep(2)

    def test_actuator_command_callback_cda_gda(self):
        """
        Ensure that incoming ActuatorData messages on CDA and GDA topics
        are converted and forwarded to the listener.
        """
        self.assertTrue(self.mcc.connectClient())
        sleep(1)

        actuatorData = ActuatorData()
        payload = DataUtil().actuatorDataToJson(actuatorData)

        # Test CDA
        self.mcc.publishMessage(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, payload, qos=0)
        sleep(3)
        self.assertTrue(self.listener.listenerCalled, "Listener was not called for CDA actuator command")
        self.assertIsNotNone(self.listener.receivedData, "Listener did not receive CDA actuator data")

        # Reset listener
        self.listener.listenerCalled = False
        self.listener.receivedData = None

        # Test GDA
        self.mcc.publishMessage(ResourceNameEnum.GDA_ACTUATOR_CMD_RESOURCE, payload, qos=0)
        sleep(3)
        self.assertTrue(self.listener.listenerCalled, "Listener was not called for GDA actuator command")
        self.assertIsNotNone(self.listener.receivedData, "Listener did not receive GDA actuator data")

    def test_subscribe_unsubscribe(self):
        self.assertTrue(self.mcc.connectClient())
        sleep(1)

        topics = [
            ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
            ResourceNameEnum.GDA_ACTUATOR_CMD_RESOURCE
        ]

        for topic in topics:
            result = self.mcc.subscribeToTopic(topic, self.listener.handleActuatorCommandMessage)
            self.assertTrue(result, f"Failed to subscribe to {topic}")

            result = self.mcc.unsubscribeFromTopic(topic)
            self.assertTrue(result, f"Failed to unsubscribe from {topic}")


if __name__ == "__main__":
    unittest.main()
