# SensorAdapterManager.py
#
# Part of Programming the Internet of Things project (MIT License)
#####

import logging
from apscheduler.schedulers.background import BackgroundScheduler

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

# Emulator imports
from programmingtheiot.cda.emulated.HumiditySensorEmulatorTask import HumiditySensorEmulatorTask
from programmingtheiot.cda.emulated.PressureSensorEmulatorTask import PressureSensorEmulatorTask
from programmingtheiot.cda.emulated.TemperatureSensorEmulatorTask import TemperatureSensorEmulatorTask

# Simulator imports
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask
from programmingtheiot.cda.sim.PressureSensorSimTask import PressureSensorSimTask
from programmingtheiot.cda.sim.TemperatureSensorSimTask import TemperatureSensorSimTask


class SensorAdapterManager(object):
    """
    SensorAdapterManager implementation for managing simulated/emulated sensors.
    """

    def __init__(self):
        self.configUtil = ConfigUtil()
        self.pollRate = self.configUtil.getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )

        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )

        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET
        )

        if self.pollRate <= 0:
            self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES

        # Scheduler for telemetry
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.handleTelemetry,
            'interval',
            seconds=self.pollRate,
            max_instances=2,
            coalesce=True,
            misfire_grace_time=15
        )

        self.dataMsgListener = None
        self.humidityAdapter = None
        self.pressureAdapter = None
        self.tempAdapter = None

        self._initEnvironmentalSensorTasks()

        if self.useEmulator:
            logging.info("SensorAdapterManager: Using sensor emulators.")
        else:
            logging.info("SensorAdapterManager: Using sensor simulators.")

    def _initEnvironmentalSensorTasks(self):
        if self.useEmulator:
            self.humidityAdapter = HumiditySensorEmulatorTask()
            self.pressureAdapter = PressureSensorEmulatorTask()
            self.tempAdapter = TemperatureSensorEmulatorTask()
        else:
            humidityFloor = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.HUMIDITY_SIM_FLOOR_KEY,
                defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY
            )
            humidityCeiling = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.HUMIDITY_SIM_CEILING_KEY,
                defaultVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
            )

            pressureFloor = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.PRESSURE_SIM_FLOOR_KEY,
                defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE
            )
            pressureCeiling = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.PRESSURE_SIM_CEILING_KEY,
                defaultVal=SensorDataGenerator.HI_NORMAL_ENV_PRESSURE
            )

            tempFloor = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.TEMP_SIM_FLOOR_KEY,
                defaultVal=SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP
            )
            tempCeiling = self.configUtil.getFloat(
                section=ConfigConst.CONSTRAINED_DEVICE,
                key=ConfigConst.TEMP_SIM_CEILING_KEY,
                defaultVal=SensorDataGenerator.HI_NORMAL_INDOOR_TEMP
            )

            self.dataGenerator = SensorDataGenerator()
            humidityData = self.dataGenerator.generateDailyEnvironmentHumidityDataSet(
                minValue=humidityFloor, maxValue=humidityCeiling, useSeconds=False
            )
            pressureData = self.dataGenerator.generateDailyEnvironmentPressureDataSet(
                minValue=pressureFloor, maxValue=pressureCeiling, useSeconds=False
            )
            tempData = self.dataGenerator.generateDailyIndoorTemperatureDataSet(
                minValue=tempFloor, maxValue=tempCeiling, useSeconds=False
            )

            self.humidityAdapter = HumiditySensorSimTask(dataSet=humidityData)
            self.pressureAdapter = PressureSensorSimTask(dataSet=pressureData)
            self.tempAdapter = TemperatureSensorSimTask(dataSet=tempData)

    def handleTelemetry(self):
        if not self.humidityAdapter or not self.pressureAdapter or not self.tempAdapter:
            logging.warning("SensorAdapterManager: Adapters not initialized, skipping telemetry.")
            return

        humidityData = self.humidityAdapter.generateTelemetry()
        pressureData = self.pressureAdapter.generateTelemetry()
        tempData = self.tempAdapter.generateTelemetry()

        humidityData.setLocationID(self.locationID)
        pressureData.setLocationID(self.locationID)
        tempData.setLocationID(self.locationID)

        logging.debug(f'Generated humidity data: {humidityData}')
        logging.debug(f'Generated pressure data: {pressureData}')
        logging.debug(f'Generated temp data: {tempData}')

        if self.dataMsgListener:
            self.dataMsgListener.handleSensorMessage(humidityData)
            self.dataMsgListener.handleSensorMessage(pressureData)
            self.dataMsgListener.handleSensorMessage(tempData)

    def setDataMessageListener(self, listener: IDataMessageListener):
        if listener:
            self.dataMsgListener = listener

    def startManager(self) -> bool:
        logging.info("Started SensorAdapterManager.")
        if not self.scheduler.running:
            self.scheduler.start()
            return True
        else:
            logging.info("SensorAdapterManager scheduler already started. Ignoring.")
            return False

    def stopManager(self) -> bool:
        logging.info("Stopped SensorAdapterManager.")
        try:
            self.scheduler.shutdown()
            return True
        except Exception:
            logging.info("SensorAdapterManager scheduler already stopped. Ignoring.")
            return False
