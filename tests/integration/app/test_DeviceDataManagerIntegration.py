#####
#
# Integration test for DeviceDataManager
# Programming the Internet of Things (MIT License)
#
#####

import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DeviceDataManagerIntegrationTest(unittest.TestCase):
    """
    Integration test for DeviceDataManager.

    This test verifies:
    - Temperature, Humidity, and Pressure SensorData are handled and published.
    - SystemPerformanceData is also sent to the GDA.
    - MQTT traffic can be observed in GDA logs or mosquitto logs.

    NOTE:
        SenseHAT emulator must be running if ENABLE_EMULATOR_KEY=True
        in PiotConfig.props.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s',
            level=logging.DEBUG
        )
        logging.info("=== DeviceDataManager Integration Test Starting ===")

    def setUp(self):
        self.ddMgr = DeviceDataManager()

    def tearDown(self):
        pass

    def testDeviceDataMgrTimedIntegration(self):
        logging.info("Starting DeviceDataManager...")
        self.ddMgr.startManager()

        # -------------------------------------------------------------------
        # SEND TEMPERATURE SENSOR DATA
        # -------------------------------------------------------------------
        temp = SensorData()
        temp.setName("TemperatureSensor")
        temp.setTypeID(ConfigConst.TEMP_SENSOR_TYPE)
        temp.setValue(30.5)  # Over typical threshold

        logging.info("Sending Temperature SensorData: %s", temp)
        self.ddMgr.handleSensorMessage(temp)

        # -------------------------------------------------------------------
        # SEND HUMIDITY SENSOR DATA
        # -------------------------------------------------------------------
        humidity = SensorData()
        humidity.setName("HumiditySensor")
        humidity.setTypeID(ConfigConst.HUMIDITY_SENSOR_TYPE)
        humidity.setValue(55.2)  # Normal humidity example

        logging.info("Sending Humidity SensorData: %s", humidity)
        self.ddMgr.handleSensorMessage(humidity)

        # -------------------------------------------------------------------
        # SEND PRESSURE SENSOR DATA
        # -------------------------------------------------------------------
        pressure = SensorData()
        pressure.setName("PressureSensor")
        pressure.setTypeID(ConfigConst.PRESSURE_SENSOR_TYPE)
        pressure.setValue(1008.4)  # Normal atmospheric pressure

        logging.info("Sending Pressure SensorData: %s", pressure)
        self.ddMgr.handleSensorMessage(pressure)

        # -------------------------------------------------------------------
        # SEND SYSTEM PERFORMANCE DATA
        # -------------------------------------------------------------------
        sysPerf = SystemPerformanceData()
        sysPerf.setCpuUtilization(22.0)
        sysPerf.setMemoryUtilization(48.0)

        logging.info("Sending SystemPerformanceData: %s", sysPerf)
        self.ddMgr.handleSystemPerformanceMessage(sysPerf)

        # -------------------------------------------------------------------
        # WAIT FOR MQTT TRAFFIC
        # -------------------------------------------------------------------
        logging.info("Waiting 30 seconds for MQTT traffic to complete...")
        sleep(30)

        logging.info("Stopping DeviceDataManager...")
        self.ddMgr.stopManager()

        logging.info("=== Integration Test Completed Successfully ===")


if __name__ == "__main__":
    unittest.main()
