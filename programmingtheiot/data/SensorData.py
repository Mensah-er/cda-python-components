#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.BaseIotData import BaseIotData


class SensorData(BaseIotData):
	"""
	Implementation of SensorData derived from BaseIotData.
	Represents sensor readings such as temperature, humidity, etc.
	"""

	def __init__(self, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, name = ConfigConst.NOT_SET, d = None):
		super(SensorData, self).__init__(name = name, typeID = typeID, d = d)

		self.value = ConfigConst.DEFAULT_VAL
		self.avgValue = ConfigConst.DEFAULT_VAL
		self.minValue = ConfigConst.DEFAULT_VAL
		self.maxValue = ConfigConst.DEFAULT_VAL
		self.sampleCount = 0

	def getValue(self) -> float:
		return self.value

	def getAverageValue(self) -> float:
		return self.avgValue

	def getMinValue(self) -> float:
		return self.minValue

	def getMaxValue(self) -> float:
		return self.maxValue

	def getSampleCount(self) -> int:
		return self.sampleCount

	def addValue(self, val: float):
		"""
		Adds a new value and updates min, max, avg, and count.
		"""
		self.value = val
		if self.sampleCount == 0:
			self.minValue = val
			self.maxValue = val
			self.avgValue = val
		else:
			if val < self.minValue:
				self.minValue = val
			if val > self.maxValue:
				self.maxValue = val

			self.avgValue = ((self.avgValue * self.sampleCount) + val) / (self.sampleCount + 1)

		self.sampleCount += 1
		self.updateTimeStamp()

	def setValue(self, val: float):
		self.value = val
		self.updateTimeStamp()

	def _handleUpdateData(self, data):
		if data and isinstance(data, SensorData):
			self.value = data.getValue()
			self.avgValue = data.getAverageValue()
			self.minValue = data.getMinValue()
			self.maxValue = data.getMaxValue()
			self.sampleCount = data.getSampleCount()

	def __str__(self):
		parentStr = super(SensorData, self).__str__()
		return parentStr + f",value={self.value},avg={self.avgValue},min={self.minValue},max={self.maxValue},samples={self.sampleCount}"
