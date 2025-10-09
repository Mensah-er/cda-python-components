#####
# 
# This class is part of the Programming the Internet of Things
<<<<<<< HEAD
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
=======
# project, and is available via the MIT License.
>>>>>>> d424d64 (cda-python-components)
# 

import logging
import unittest
<<<<<<< HEAD

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask

class HumiditySensorSimTaskTest(unittest.TestCase):
	"""
	This test case class contains very basic unit tests for
	HumiditySensorSimTask. It should not be considered complete,
	but serve as a starting point for the student implementing
	additional functionality within their Programming the IoT
	environment.
	"""
	
	@classmethod
	def setUpClass(self):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Testing HumiditySensorSimTask class...")
		self.hSimTask = HumiditySensorSimTask()
		
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testGenerateTelemetry(self):
		sd = self.hSimTask.generateTelemetry()
		
		if sd:
			logging.info("SensorData: " + str(sd))
		else:
			logging.warning("SensorData is None.")
			
	#@unittest.skip("Ignore for now.")
	def testGetTelemetryValue(self):
		val = self.hSimTask.getTelemetryValue()
		logging.info("Humidity data: %f", val)
		self.assertGreater(val, ConfigConst.DEFAULT_VAL)

if __name__ == "__main__":
	unittest.main()
	
=======
import programmingtheiot.common.ConfigConst as ConfigConst

# Import the correct class
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorEmulatorTask

class HumiditySensorEmulatorTaskTest(unittest.TestCase):
    """
    Unit test for the HumiditySensorEmulatorTask class.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', 
            level=logging.DEBUG
        )
        logging.info("Testing HumiditySensorEmulatorTask class...")
        cls.hEmuTask = HumiditySensorEmulatorTask()

    def testGenerateTelemetry(self):
        """Test that telemetry is generated correctly."""
        sd = self.hEmuTask.generateTelemetry()
        self.assertIsNotNone(sd, "SensorData should not be None")
        logging.info("SensorData: %s", sd)

    def testGetTelemetryValue(self):
        """Test that the telemetry value is within a reasonable range."""
        val = self.hEmuTask.getTelemetryValue()
        logging.info("Humidity data: %f", val)
        self.assertGreater(val, ConfigConst.DEFAULT_VAL)

if __name__ == "__main__":
    unittest.main()

>>>>>>> d424d64 (cda-python-components)
