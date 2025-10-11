# HumidifierActuatorSimTask.py

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HumidifierActuatorSimTask(BaseActuatorSimTask):
    """
    Simple actuator simulator for a humidifier.
    """

    def __init__(self):
        super(HumidifierActuatorSimTask, self).__init__(
            name=ConfigConst.HUMIDIFIER_ACTUATOR_NAME,
            typeID=ConfigConst.HUMIDIFIER_ACTUATOR_TYPE,
            simpleName="HUMIDIFIER"
        )
