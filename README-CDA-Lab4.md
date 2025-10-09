# Constrained Device Application (Connected Devices)

## Lab Module 04

Be sure to implement all the PIOT-CDA-* issues (requirements) listed at [PIOT-INF-04-001 - Lab Module 04](https://github.com/orgs/programming-the-iot/projects/1#column-10488386).

### Description

NOTE: Include two full paragraphs describing your implementation approach by answering the questions listed below.

What does your implementation do? 
This module implements the emulator-based sensor tasks for temperature, pressure, and humidity using the Sense HAT emulator. Each sensor task class (TemperatureSensorEmulatorTask, PressureSensorEmulatorTask, and HumiditySensorEmulatorTask) extends the BaseSensorSimTask and overrides the generateTelemetry() method to obtain real-time sensor data from the emulator. The implementation ensures that telemetry is generated correctly, including sensor values, timestamps, and relevant metadata, for testing and simulation purposes without the need for actual hardware.

How does your implementation work?
The implementation initializes the Sense HAT emulator by loading configuration flags from PiotConfig.props. Each emulator task creates an instance of SenseHAT(emulate=True) and retrieves telemetry data using the .environ property for temperature, pressure, and humidity. The data is stored in SensorData objects and updated in the latestSensorData attribute of each task. Integration tests verify that the emulator responds with expected ranges and formats for telemetry values, ensuring correctness and allowing for smooth development of higher-level CDA components without requiring physical sensors.

### Code Repository and Branch

NOTE: Be sure to include the branch (e.g. https://github.com/programming-the-iot/python-components/tree/alpha001).

URL: 

### UML Design Diagram(s)

NOTE: Include one or more UML designs representing your solution. It's expected each
diagram you provide will look similar to, but not the same as, its counterpart in the
book [Programming the IoT](https://learning.oreilly.com/library/view/programming-the-internet/9781492081401/).


### Unit Tests Executed

NOTE: TA's will execute your unit tests. You only need to list each test case below
(e.g. ConfigUtilTest, DataUtilTest, etc). Be sure to include all previous tests, too,
since you need to ensure you haven't introduced regressions.

-test_TemperatureEmulatorTask

-test_PressureEmulatorTask

-test_HumidityEmulatorTask
- 
- 

### Integration Tests Executed

NOTE: TA's will execute most of your integration tests using their own environment, with
some exceptions (such as your cloud connectivity tests). In such cases, they'll review
your code to ensure it's correct. As for the tests you execute, you only need to list each
test case below (e.g. SensorSimAdapterManagerTest, DeviceDataManagerTest, etc.)

-TemperatureEmulatorTaskTest
-PressureEmulatorTaskTest
-HumidityEmulatorTaskTest
- 

EOF.
