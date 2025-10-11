import logging
import smbus2 as smbus

from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
import programmingtheiot.common.ConfigConst as ConfigConst


class HumidityI2cSensorAdapterTask(BaseSensorSimTask):
    """
    Humidity sensor adapter using I2C (Sense HAT HTS221).
    """

    def __init__(self):
        super(HumidityI2cSensorAdapterTask, self).__init__(
            name=ConfigConst.HUMIDITY_SENSOR_NAME,
            typeID=ConfigConst.HUMIDITY_SENSOR_TYPE,
            minVal=0.0,
            maxVal=100.0
        )

        self.sensorType = ConfigConst.HUMIDITY_SENSOR_TYPE
        self.humidAddr = 0x5F  # HTS221 default I2C address
        self.i2cBus = smbus.SMBus(1)  # Only use I2C bus 1 on Pi

        # Initialize the sensor (example)
        try:
            self.i2cBus.write_byte_data(self.humidAddr, 0x20, 0x85)  # CTRL_REG1: enable sensor
        except Exception as e:
            logging.error(f"Error initializing Humidity sensor: {e}")

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        # TODO: Implement proper I2C read and convert to float
        sensorVal = self.getTelemetryValue()
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        return sensorData

    def getTelemetryValue(self) -> float:
        # TODO: Read from I2C and return humidity value
        return 0.0
