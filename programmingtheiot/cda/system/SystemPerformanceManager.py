import threading
import time
import logging
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.cda.system.SystemCpuUtilTask import SystemCpuUtilTask
from programmingtheiot.cda.system.SystemMemUtilTask import SystemMemUtilTask
from programmingtheiot.common.IDataMessageListener import IDataMessageListener


class SystemPerformanceManager:
    """
    Manages system performance telemetry collection (CPU and Memory utilization).
    Collects data and optionally forwards it to a registered IDataMessageListener.
    """

    def __init__(self):
        self.cpuUtilTask = SystemCpuUtilTask()
        self.memUtilTask = SystemMemUtilTask()
        self.dataMsgListener = None
        self.cpuUtilPct = 0.0
        self.memUtilPct = 0.0
        self.locationID = "CDA_DEVICE_01"

        self.isRunning = False
        self.pollRateSec = 5.0
        self._pollingThread = None

        logging.info("SystemPerformanceManager initialized.")

    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        if listener:
            self.dataMsgListener = listener
            logging.info("Data message listener successfully set.")
            return True
        else:
            logging.warning("Invalid listener. None set.")
            return False

    def handleTelemetry(self):
        try:
            self.cpuUtilPct = self.cpuUtilTask.getTelemetryValue()
            self.memUtilPct = self.memUtilTask.getTelemetryValue()

            sysPerfData = SystemPerformanceData()
            sysPerfData.setLocationID(self.locationID)
            sysPerfData.setCpuUtilization(self.cpuUtilPct)
            sysPerfData.setMemoryUtilization(self.memUtilPct)

            if self.dataMsgListener:
                self.dataMsgListener.handleSystemPerformanceMessage(data=sysPerfData)
                logging.info("System performance data sent to listener.")
            else:
                logging.debug("No listener configured; telemetry retained locally.")

        except Exception as e:
            logging.exception("Error while collecting telemetry data: %s", str(e))

    def startManager(self):
        """
        Starts periodic telemetry collection.
        """
        if not self.isRunning:
            logging.info("Starting SystemPerformanceManager telemetry collection thread.")
            self.isRunning = True
            self._pollingThread = threading.Thread(target=self._run, daemon=True)
            self._pollingThread.start()
        else:
            logging.info("SystemPerformanceManager is already running.")

    def stopManager(self):
        """
        Stops periodic telemetry collection.
        """
        if self.isRunning:
            logging.info("Stopping SystemPerformanceManager telemetry collection thread.")
            self.isRunning = False
            if self._pollingThread:
                self._pollingThread.join(timeout=2)
                self._pollingThread = None
        else:
            logging.info("SystemPerformanceManager is not running.")

    def _run(self):
        """
        Internal loop that periodically collects telemetry.
        """
        while self.isRunning:
            self.handleTelemetry()
            time.sleep(self.pollRateSec)
