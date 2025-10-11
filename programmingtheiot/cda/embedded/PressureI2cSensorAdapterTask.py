import logging
import smbus2 as smbus

from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
import programmingtheiot.common.ConfigConst as ConfigConst


class PressureI2cSensorAdapterTask(BaseSensorSimTask):
    """
    Pressure sensor adapter using I2C (Sense HAT LPS25H).
    """

    def __init__(self):
        super(PressureI2cSensorAdapterTask, self).__init__(
            name=ConfigConst.PRESSURE_SENSOR_NAME,
            typeID=ConfigConst.PRESSURE_SENSOR_TYPE,
            minVal=900.0,
            maxVal=1100.0
        )

        self.sensorType = ConfigConst.PRESSURE_SENSOR_TYPE
        self.pressAddr = 0x5C  # LPS25H default I2C address
        self.i2cBus = smbus.SMBus(1)

        try:
            self.i2cBus.write_byte_data(self.pressAddr, 0x20, 0x90)  # CTRL_REG1: enable sensor
        except Exception as e:
            logging.error(f"Error initializing Pressure sensor: {e}")

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        sensorVal = self.getTelemetryValue()
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        return sensorData

    def getTelemetryValue(self) -> float:
        # TODO: Read from I2C and return pressure value
        return 0.0
