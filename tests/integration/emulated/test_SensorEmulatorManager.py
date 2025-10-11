# test_SensorEmulatorManager.py
#
# Integration test for SensorAdapterManager using Sense HAT emulator.
# Requires sense_emu_gui to be installed and optionally running.
#####

import logging
import unittest
from time import sleep
import os
import sys
import subprocess

# Ensure project root is in PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener


class SensorEmulatorManagerTest(unittest.TestCase):
    """
    Integration test for SensorAdapterManager using Sense HAT emulator.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s',
            level=logging.DEBUG
        )
        # Reduce PNG debug noise from PIL
        logging.getLogger('PngImagePlugin').setLevel(logging.WARNING)

        logging.info("Testing SensorAdapterManager class [using SenseHAT emulator]...")

        # Try starting Sense HAT emulator GUI if available
        try:
            subprocess.Popen(["sense_emu_gui"])
        except FileNotFoundError:
            logging.warning("Sense HAT emulator GUI not found, ensure it's installed.")

        # Initialize SensorAdapterManager and listener
        cls.defaultMsgListener = DefaultDataMessageListener()
        cls.sensorAdapterMgr = SensorAdapterManager()
        cls.sensorAdapterMgr.setDataMessageListener(cls.defaultMsgListener)

    def testRunAllSimulators(self):
        """Start the SensorAdapterManager, run for a short while, then stop."""
        logging.info("Starting SensorAdapterManager...")
        self.sensorAdapterMgr.startManager()

        # Run the manager for a few seconds (short for test purposes)
        sleep(5)

        logging.info("Stopping SensorAdapterManager...")
        self.sensorAdapterMgr.stopManager()


if __name__ == "__main__":
    unittest.main()
