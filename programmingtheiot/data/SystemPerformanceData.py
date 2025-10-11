#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.BaseIotData import BaseIotData


class SystemPerformanceData(BaseIotData):
	"""
	Implementation of SystemPerformanceData derived from BaseIotData.
	Represents CPU, memory, and disk utilization stats.
	"""

	def __init__(self, name = ConfigConst.SYSTEM_PERF_NAME, typeID = ConfigConst.SYSTEM_PERF_TYPE, d = None):
		super(SystemPerformanceData, self).__init__(name = name, typeID = typeID, d = d)

		self.cpuUtil = ConfigConst.DEFAULT_VAL
		self.memUtil = ConfigConst.DEFAULT_VAL
		self.diskUtil = ConfigConst.DEFAULT_VAL

	def getCpuUtilization(self) -> float:
		return self.cpuUtil

	def getMemoryUtilization(self) -> float:
		return self.memUtil

	def getDiskUtilization(self) -> float:
		return self.diskUtil

	def setCpuUtilization(self, val: float):
		self.cpuUtil = val
		self.updateTimeStamp()

	def setMemoryUtilization(self, val: float):
		self.memUtil = val
		self.updateTimeStamp()

	def setDiskUtilization(self, val: float):
		self.diskUtil = val
		self.updateTimeStamp()

	def _handleUpdateData(self, data):
		if data and isinstance(data, SystemPerformanceData):
			self.cpuUtil = data.getCpuUtilization()
			self.memUtil = data.getMemoryUtilization()
			self.diskUtil = data.getDiskUtilization()

	def __str__(self):
		parentStr = super(SystemPerformanceData, self).__str__()
		return parentStr + f",cpu={self.cpuUtil},mem={self.memUtil},disk={self.diskUtil}"
