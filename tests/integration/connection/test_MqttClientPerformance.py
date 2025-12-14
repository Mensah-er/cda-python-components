# tests/integration/connection/test_MqttClientPerformance.py

import unittest
import time
import logging
import json

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum


class TestMqttClientPerformance(unittest.TestCase):
    NS_IN_MILLIS = 1000000
    MAX_TEST_RUNS = 10000  # Lab 10 requirement

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s',
            level=logging.INFO
        )

    def setUp(self):
        self.mqttClient = MqttClientConnector(clientID="CDAMqttClientPerformanceTest001")

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
    # HELPER
    # ------------------------------------------------------------------------
    def _execTestPublish(self, maxTestRuns: int, qos: int):
        self.assertTrue(self.mqttClient.connectClient())
        dataUtil = DataUtil()

        # Payloads
        sensorPayload = dataUtil.sensorDataToJson(SensorData())
        actuatorPayload = dataUtil.actuatorDataToJson(ActuatorData())

        # Simulated realistic payloads
        systemPerfPayload = json.dumps({
            "cpu": 25.5,
            "mem": 512,
            "disk": 10240
        })

        mgmtStatusPayload = json.dumps({
            "status": "OK",
            "uptime": 3600
        })

        mgmtCmdPayload = json.dumps({
            "cmd": "RESTART",
            "timestamp": time.time()
        })

        updateNotifPayload = json.dumps({
            "version": "1.0.1",
            "msg": "Update available"
        })

        registrationPayload = json.dumps({
            "deviceId": "device123",
            "timestamp": time.time()
        })

        # Topics by type
        sensor_topics = [ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, ResourceNameEnum.GDA_SENSOR_MSG_RESOURCE]
        actuator_cmd_topics = [ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, ResourceNameEnum.GDA_ACTUATOR_CMD_RESOURCE]
        actuator_resp_topics = [ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE, ResourceNameEnum.GDA_ACTUATOR_RESPONSE_RESOURCE]
        system_perf_topics = [ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, ResourceNameEnum.GDA_SYSTEM_PERF_MSG_RESOURCE]
        mgmt_status_topics = [ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, ResourceNameEnum.GDA_MGMT_STATUS_MSG_RESOURCE]
        mgmt_cmd_topics = [ResourceNameEnum.CDA_MGMT_STATUS_CMD_RESOURCE, ResourceNameEnum.GDA_MGMT_CMD_RESOURCE]
        update_notification_topics = [ResourceNameEnum.CDA_UPDATE_NOTIFICATIONS_RESOURCE, ResourceNameEnum.GDA_UPDATE_NOTIFICATIONS_MSG_RESOURCE]
        registration_topics = [ResourceNameEnum.CDA_REGISTRATION_REQUEST_RESOURCE, ResourceNameEnum.GDA_REGISTRATION_REQUEST_RESOURCE]

        topic_map = {}
        for t in sensor_topics:
            topic_map[t] = sensorPayload
        for t in actuator_cmd_topics + actuator_resp_topics:
            topic_map[t] = actuatorPayload
        for t in system_perf_topics:
            topic_map[t] = systemPerfPayload
        for t in mgmt_status_topics:
            topic_map[t] = mgmtStatusPayload
        for t in mgmt_cmd_topics:
            topic_map[t] = mgmtCmdPayload
        for t in update_notification_topics:
            topic_map[t] = updateNotifPayload
        for t in registration_topics:
            topic_map[t] = registrationPayload

        all_topics = list(topic_map.keys())

        # Run test
        startTime = time.time_ns()
        for _ in range(maxTestRuns):
            for topic in all_topics:
                self.mqttClient.publishMessage(
                    resource=topic,
                    msg=topic_map[topic],
                    qos=qos
                )
        endTime = time.time_ns()
        self.assertTrue(self.mqttClient.disconnectClient())

        total_topics = len(all_topics)
        elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
        logging.info(
            f"Publish - QoS {qos} [{maxTestRuns} runs, {total_topics} topics] with realistic payloads: {elapsedMillis:.2f} ms"
        )
