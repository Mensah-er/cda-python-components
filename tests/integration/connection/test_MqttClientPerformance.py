# tests/integration/connection/test_MqttClientPerformance.py

import unittest
import time
import logging

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum


class TestMqttClientPerformance(unittest.TestCase):
    NS_IN_MILLIS = 1000000
    MAX_TEST_RUNS = 10000  # Lab 10 requires 10,000 messages

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s',
            level=logging.INFO
        )

    def setUp(self):
        # Use a unique client ID for this test
        self.mqttClient = MqttClientConnector(client_id='CDAMqttClientPerformanceTest001')

    def tearDown(self):
        self.mqttClient.disconnectClient()

    def testConnectAndDisconnect(self):
        startTime = time.time_ns()
        self.assertTrue(self.mqttClient.connectClient())
        self.assertTrue(self.mqttClient.disconnectClient())
        endTime = time.time_ns()

        elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
        logging.info(f"Connect and Disconnect: {elapsedMillis:.2f} ms")

    def testPublishQoS0(self):
        self._execTestPublish(self.MAX_TEST_RUNS, 0)

    def testPublishQoS1(self):
        self._execTestPublish(self.MAX_TEST_RUNS, 1)

    def testPublishQoS2(self):
        self._execTestPublish(self.MAX_TEST_RUNS, 2)

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    def _execTestPublish(self, maxTestRuns: int, qos: int):
        self.assertTrue(self.mqttClient.connectClient())

        sensorData = SensorData()
        payload = DataUtil().sensorDataToJson(sensorData)

        startTime = time.time_ns()
        for _ in range(maxTestRuns):
            self.mqttClient.publishMessage(
                resource=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE,
                msg=payload,
                qos=qos
            )
        endTime = time.time_ns()

        self.assertTrue(self.mqttClient.disconnectClient())
        elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
        logging.info(f"Publish message - QoS {qos} [{maxTestRuns}]: {elapsedMillis:.2f} ms")
