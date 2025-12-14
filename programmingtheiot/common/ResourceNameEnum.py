# /piot-python-components/programmingtheiot/common/ResourceNameEnum.py

from enum import Enum
import programmingtheiot.common.ConfigConst as ConfigConst

class ResourceNameEnum(Enum):
    """
    Unified resource names used across CDA and GDA.
    Mirrors the Java ResourceNameEnum and includes GDA-specific topics.
    """

    # --- CDA Resources ---
    CDA_SENSOR_MSG_RESOURCE           = ConfigConst.SENSOR_MSG
    CDA_ACTUATOR_CMD_RESOURCE         = ConfigConst.ACTUATOR_CMD
    CDA_ACTUATOR_RESPONSE_RESOURCE    = ConfigConst.ACTUATOR_RESPONSE
    CDA_SYSTEM_PERF_MSG_RESOURCE      = ConfigConst.SYSTEM_PERF_MSG
    CDA_MGMT_STATUS_MSG_RESOURCE      = ConfigConst.MGMT_STATUS_MSG
    CDA_MGMT_STATUS_CMD_RESOURCE      = ConfigConst.MGMT_STATUS_CMD
    CDA_UPDATE_NOTIFICATIONS_RESOURCE = ConfigConst.UPDATE_NOTIFICATIONS_MSG
    CDA_REGISTRATION_REQUEST_RESOURCE = ConfigConst.RESOURCE_REGISTRATION_REQUEST

    # --- GDA Resources (shared with CDA) ---
    GDA_SENSOR_MSG_RESOURCE           = ConfigConst.SENSOR_MSG
    GDA_ACTUATOR_CMD_RESOURCE         = ConfigConst.ACTUATOR_CMD
    GDA_ACTUATOR_RESPONSE_RESOURCE    = ConfigConst.ACTUATOR_RESPONSE
    GDA_SYSTEM_PERF_MSG_RESOURCE      = ConfigConst.SYSTEM_PERF_MSG
    GDA_MGMT_STATUS_MSG_RESOURCE      = ConfigConst.MGMT_STATUS_MSG
    GDA_MGMT_CMD_RESOURCE             = ConfigConst.MGMT_STATUS_CMD
    GDA_UPDATE_NOTIFICATIONS_MSG_RESOURCE = ConfigConst.UPDATE_NOTIFICATIONS_MSG
    GDA_REGISTRATION_REQUEST_RESOURCE = ConfigConst.RESOURCE_REGISTRATION_REQUEST

    # --- Aliases for backwards compatibility ---
    CDA_SENSOR_MSG      = ConfigConst.SENSOR_MSG
    CDA_ACTUATOR_CMD    = ConfigConst.ACTUATOR_CMD
    CDA_SYSTEM_PERF_MSG = ConfigConst.SYSTEM_PERF_MSG

    GDA_SENSOR_MSG      = ConfigConst.SENSOR_MSG
    GDA_ACTUATOR_CMD    = ConfigConst.ACTUATOR_CMD
    GDA_SYSTEM_PERF_MSG = ConfigConst.SYSTEM_PERF_MSG

    # --- Default fallback ---
    DEFAULT = "DEFAULT"

    @staticmethod
    def get_enum_from_value(val: str):
        """
        Returns the matching ResourceNameEnum for a string value, or DEFAULT if not found.
        """
        for res in ResourceNameEnum:
            if res.value == val:
                return res
        return ResourceNameEnum.DEFAULT

    def get_resource_name(self) -> str:
        """
        Returns the string value of the enum.
        """
        return self.value
