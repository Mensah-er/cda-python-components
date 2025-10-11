# test_EmbeddedSensorAdapter.py
#
# Integration test for Embedded I2C Sensor Adapters.
##### 

import logging
import unittest
from time import sleep
import os
import sys

# Ensure project root is in PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from programmingtheiot.cda.embedded.HumidityI2cSensorAdapterTask import HumidityI2cSensorAdapterTask
from programmingtheiot.cda.embedded.PressureI2cSensorAdapterTask import PressureI2cSensorAdapterTask
from programmingtheiot.cda.embedded.TemperatureI2cSensorAdapterTask import TemperatureI2cSensorAdapterTask
from programmingtheiot.data.SensorData import SensorData


class EmbeddedSensorAdapterTest(unittest.TestCase):
    """
    Integration test for I2C-based Humidity, Pressure, and Temperature sensor adapters.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s',
            level=logging.DEBUG
        )
        logging.info("Testing Embedded I2C Sensor Adapters...")

    def setUp(self):
        # Initialize adapters
        self.humidityAdapter = HumidityI2cSensorAdapterTask()
        self.pressureAdapter = PressureI2cSensorAdapterTask()
        self.tempAdapter = TemperatureI2cSensorAdapterTask()

    def test_humidity_telemetry(self):
        data: SensorData = self.humidityAdapter.generateTelemetry()
        self.assertIsInstance(data, SensorData)
        logging.info(f"Humidity reading: {data.getValue()}")
        self.assertTrue(0 <= data.getValue() <= 100)

    def test_pressure_telemetry(self):
        data: SensorData = self.pressureAdapter.generateTelemetry()
        self.assertIsInstance(data, SensorData)
        logging.info(f"Pressure reading: {data.getValue()}")
        self.assertTrue(300 <= data.getValue() <= 1100)

    def test_temperature_telemetry(self):
        data: SensorData = self.tempAdapter.generateTelemetry()
        self.assertIsInstance(data, SensorData)
        logging.info(f"Temperature reading: {data.getValue()}")
        self.assertTrue(-40 <= data.getValue() <= 85)

    def test_get_telemetry_value(self):
        # Ensure getTelemetryValue returns a float
        self.assertIsInstance(self.humidityAdapter.getTelemetryValue(), float)
        self.assertIsInstance(self.pressureAdapter.getTelemetryValue(), float)
        self.assertIsInstance(self.tempAdapter.getTelemetryValue(), float)


if __name__ == "__main__":
    unittest.main()

