# HvacActuatorSimTask.py

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HvacActuatorSimTask(BaseActuatorSimTask):
    """
    Simple actuator simulator for an HVAC system.
    """

    def __init__(self):
        super(HvacActuatorSimTask, self).__init__(
            name=ConfigConst.HVAC_ACTUATOR_NAME,
            typeID=ConfigConst.HVAC_ACTUATOR_TYPE,
            simpleName="HVAC"
        )
