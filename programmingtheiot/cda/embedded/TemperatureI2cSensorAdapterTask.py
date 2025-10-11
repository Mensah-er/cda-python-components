import logging
import smbus2 as smbus

from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
import programmingtheiot.common.ConfigConst as ConfigConst


class TemperatureI2cSensorAdapterTask(BaseSensorSimTask):
    """
    Temperature sensor adapter using I2C (Sense HAT HTS221/LPS25H).
    """

    def __init__(self):
        super(TemperatureI2cSensorAdapterTask, self).__init__(
            name=ConfigConst.TEMP_SENSOR_NAME,
            typeID=ConfigConst.TEMP_SENSOR_TYPE,
            minVal=-20.0,
            maxVal=50.0
        )

        self.sensorType = ConfigConst.TEMP_SENSOR_TYPE
        self.tempAddr = 0x5F  # HTS221 default I2C address
        self.i2cBus = smbus.SMBus(1)

        try:
            self.i2cBus.write_byte_data(self.tempAddr, 0x20, 0x85)  # CTRL_REG1: enable sensor
        except Exception as e:
            logging.error(f"Error initializing Temperature sensor: {e}")

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        sensorVal = self.getTelemetryValue()
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        return sensorData

    def getTelemetryValue(self) -> float:
        # TODO: Read from I2C and return temperature value
        return 0.0
