import logging
from importlib import import_module

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.HvacActuatorSimTask import HvacActuatorSimTask
from programmingtheiot.cda.sim.HumidifierActuatorSimTask import HumidifierActuatorSimTask


class ActuatorAdapterManager(object):
    """
    ActuatorAdapterManager manages actuator simulation and emulation tasks.
    This class dynamically loads emulator classes (Sense HAT-based) when
    the emulator is enabled in configuration.
    """

    def __init__(self, dataMsgListener: IDataMessageListener = None):
        """
        Initialize the ActuatorAdapterManager, determining whether to use
        simulators or SenseHAT emulators based on configuration settings.
        """
        self.dataMsgListener = dataMsgListener

        # Config utility for loading device configuration
        self.configUtil = ConfigUtil()

        # Check emulator/simulator flags from PiotConfig.props
        self.useEmulator = self.configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.useSimulator = self.configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_SIMULATOR_KEY
        )

        # Device and location information
        self.deviceID = self.configUtil.getProperty(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.DEVICE_ID_KEY,
            ConfigConst.NOT_SET
        )
        self.locationID = self.configUtil.getProperty(
            ConfigConst.CONSTRAINED_DEVICE,
            ConfigConst.DEVICE_LOCATION_ID_KEY,
            ConfigConst.NOT_SET
        )

        # Actuator references
        self.humidifierActuator = None
        self.hvacActuator = None
        self.ledDisplayActuator = None

        # Log active mode
        if self.useEmulator:
            logging.info("ActuatorAdapterManager: SenseHAT emulators enabled.")
        else:
            logging.info("ActuatorAdapterManager: Using software simulators.")

        # Initialize actuator tasks (either emulator or simulator)
        self._initEnvironmentalActuationTasks()

    def _initEnvironmentalActuationTasks(self):
        """
        Initialize actuator tasks based on configuration mode (emulator/simulator).
        Dynamically loads SenseHAT emulator classes when emulation is enabled.
        """
        if not self.useEmulator:
            # Load simulated actuation tasks
            self.humidifierActuator = HumidifierActuatorSimTask()
            self.hvacActuator = HvacActuatorSimTask()
            logging.info("ActuatorAdapterManager: Simulator tasks initialized.")
        else:
            try:
                # Load the Humidifier Emulator
                hueModule = import_module('programmingtheiot.cda.emulated.HumidifierEmulatorTask', 'HumidifierEmulatorTask')
                hueClazz = getattr(hueModule, 'HumidifierEmulatorTask')
                self.humidifierActuator = hueClazz()

                # Load the HVAC Emulator
                hveModule = import_module('programmingtheiot.cda.emulated.HvacEmulatorTask', 'HvacEmulatorTask')
                hveClazz = getattr(hveModule, 'HvacEmulatorTask')
                self.hvacActuator = hveClazz()

                # Load the LED Display Emulator
                leDisplayModule = import_module('programmingtheiot.cda.emulated.LedDisplayEmulatorTask', 'LedDisplayEmulatorTask')
                leClazz = getattr(leDisplayModule, 'LedDisplayEmulatorTask')
                self.ledDisplayActuator = leClazz()

                logging.info("ActuatorAdapterManager: Emulator tasks initialized successfully.")

            except Exception as e:
                logging.error(f"ActuatorAdapterManager: Failed to initialize emulator tasks. Error: {e}")

    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        """
        Set a data message listener for the actuator manager.
        """
        if listener:
            self.dataMsgListener = listener
            return True
        return False

    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        """
        Send actuator command to the appropriate actuator instance.
        This supports both simulated and emulated actuators.
        """
        if data and not data.isResponseFlagEnabled():
            if data.getLocationID() == self.locationID:
                logging.info(f"ActuatorAdapterManager: Processing actuation request for location {data.getLocationID()}")

                aType = data.getTypeID()
                responseData = None

                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                elif aType == ConfigConst.LED_DISPLAY_ACTUATOR_TYPE and self.ledDisplayActuator:
                    responseData = self.ledDisplayActuator.updateActuator(data)
                else:
                    logging.warning(f"ActuatorAdapterManager: Invalid actuator type {aType}. Ignoring command.")

                # Optional: send response data to listener
                if self.dataMsgListener and responseData:
                    self.dataMsgListener.handleActuatorCommandResponse(responseData)

                return responseData
            else:
                logging.warning(
                    f"ActuatorAdapterManager: Ignoring actuation request. "
                    f"Location mismatch - local: {self.locationID}, request: {data.getLocationID()}"
                )
        else:
            logging.warning("ActuatorAdapterManager: Empty or response-type actuator data received. Ignoring.")

        return None
