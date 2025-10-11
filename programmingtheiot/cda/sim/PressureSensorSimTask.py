from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from pisense import SenseHAT

class PressureSensorSimTask(BaseSensorSimTask):
    """
    Legacy Pressure Sensor Sim Task
    """
    def __init__(self, dataSet=None):
        super(PressureSensorSimTask, self).__init__(
            name=ConfigConst.PRESSURE_SENSOR_NAME,
            typeID=ConfigConst.PRESSURE_SENSOR_TYPE
        )
        enableEmulation = ConfigUtil().getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.sh = SenseHAT(emulate=enableEmulation)

    def generateTelemetry(self) -> SensorData:
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        sensorVal = self.sh.environ.pressure
        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData
        return sensorData

class PressureSensorEmulatorTask(PressureSensorSimTask):
    """
    Emulated Pressure Sensor Task (subclass of legacy simulator)
    """
    pass
