from enum import Enum
import programmingtheiot.common.ConfigConst as ConfigConst

class ResourceNameEnum(Enum):
    CDA_SENSOR_MSG_RESOURCE           = ConfigConst.CDA_SENSOR_DATA_MSG_RESOURCE
    CDA_ACTUATOR_CMD_RESOURCE         = ConfigConst.CDA_ACTUATOR_CMD_MSG_RESOURCE
    CDA_ACTUATOR_RESPONSE_RESOURCE    = ConfigConst.CDA_ACTUATOR_RESPONSE_MSG_RESOURCE
    CDA_MGMT_STATUS_MSG_RESOURCE      = ConfigConst.CDA_MGMT_STATUS_MSG_RESOURCE
    CDA_MGMT_STATUS_CMD_RESOURCE      = ConfigConst.CDA_MGMT_CMD_MSG_RESOURCE
    CDA_SYSTEM_PERF_MSG_RESOURCE      = ConfigConst.CDA_SYSTEM_PERF_MSG_RESOURCE
    CDA_UPDATE_NOTIFICATIONS_RESOURCE = ConfigConst.CDA_UPDATE_NOTIFICATIONS_MSG_RESOURCE
    CDA_REGISTRATION_REQUEST_RESOURCE = ConfigConst.CDA_REGISTRATION_REQUEST_RESOURCE

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
