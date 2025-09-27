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
    Manages actuator simulators (and eventually emulators).
    """

    def __init__(self, dataMsgListener: IDataMessageListener = None):
        self.dataMsgListener = dataMsgListener

        # Config utility
        self.configUtil = ConfigUtil()

        # Load configuration
        self.useSimulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.ENABLE_SIMULATOR_KEY
        )
        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.deviceID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET
        )
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET
        )

        # Actuator tasks
        self.humidifierActuator = None
        self.hvacActuator = None
        self.ledDisplayActuator = None

        # Log which mode is active
        if self.useEmulator:
            logging.info("Emulators will be used.")
        else:
            logging.info("Simulators will be used.")

        # Initialize actuator tasks
        self._initEnvironmentalActuationTasks()

    def _initEnvironmentalActuationTasks(self):
        """
        Initializes actuator simulation tasks (for now only simulators).
        """
        if not self.useEmulator:
            self.humidifierActuator = HumidifierActuatorSimTask()
            self.hvacActuator = HvacActuatorSimTask()

    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        """
        Sets the data message listener if valid.
        """
        if listener:
            self.dataMsgListener = listener
            return True
        return False

    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        """
        Trigger an actuation based on the ActuatorData instance.
        """
        if data and not data.isResponseFlagEnabled():
            # Check location ID matches this device
            if data.getLocationID() == self.locationID:
                logging.info(
                    "Actuator command received for location ID %s. Processing...", 
                    str(data.getLocationID())
                )

                aType = data.getTypeID()
                responseData = None

                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                elif aType == ConfigConst.LED_DISPLAY_ACTUATOR_TYPE and self.ledDisplayActuator:
                    responseData = self.ledDisplayActuator.updateActuator(data)
                else:
                    logging.warning(
                        "No valid actuator type. Ignoring actuation for type: %s", 
                        data.getTypeID()
                    )

                # In later lab modules, responseData may be passed to IDataMessageListener
                return responseData
            else:
                logging.warning(
                    "Location ID doesn't match. Ignoring actuation: (me) %s != (you) %s",
                    str(self.locationID),
                    str(data.getLocationID())
                )
        else:
            logging.warning("Actuator request received. Message is empty or response. Ignoring.")

        return None
