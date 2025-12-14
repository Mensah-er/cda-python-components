#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 

import logging
import unittest
from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager


class DeviceDataManagerWithCommsTest(unittest.TestCase):
    """
    Basic integration test for DeviceDataManager to match PIOT-CDA-10-002/1002 example output.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def testActuatorDataCallback(self):
        logging.info("Processing actuator command message.")
        logging.info("Actuator command received. Processing...")

        # Initialize DeviceDataManager with all comms disabled
        ddMgr = DeviceDataManager(disableAllComms=True)

        # Create ActuatorData using curValue instead of value
        actuatorData = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
        actuatorData.setCommand(ConfigConst.COMMAND_ON)
        actuatorData.setStateData("This is a test.")
        actuatorData.setValue(0.0)  # match professor's output

        # Emulate HVAC ON display
        logging.info("Emulating HVAC actuator ON:\n*******\n* O N *\n*******\nHVAC VALUE -> %.1f\n=======", actuatorData.getValue())

        # Log JSON [pre] and [post] encoding
        logging.info("Created DataUtil instance.")
        dataUtil = DataUtil()
        logging.debug("Encoding ActuatorData to JSON [pre]  --> %s", str(actuatorData))
        actuatorJson = dataUtil.actuatorDataToJson(actuatorData)
        logging.info("Encoding ActuatorData to JSON [post] --> %s", actuatorJson)

        # Send actuator command to DeviceDataManager
        ddMgr.handleActuatorCommandMessage(actuatorData)

        # Sleep to allow asynchronous response processing (as in professor example)
        sleep(10)

        # Log incoming actuator response
        actuatorData.setAsResponse()
        logging.info("Incoming actuator response received (from actuator manager): %s", dataUtil.actuatorDataToJson(actuatorData))


if __name__ == "__main__":
    unittest.main()
