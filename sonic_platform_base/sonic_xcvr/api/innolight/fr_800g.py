"""
    fr_800g.py

    Implementation of Innolight FR module specific in addition to the CMIS specification.
"""

from ...fields import consts
from ..public.cmis import CmisApi

class CmisFr800gApi(CmisApi):
    def get_transceiver_info_firmware_versions(self):
        return_dict = {"active_firmware" : "N/A", "inactive_firmware" : "N/A"}
        
        InactiveFirmware = self.get_module_inactive_firmware()
        ActiveFirmware = self.get_module_active_firmware()

        return_dict["active_firmware"] = ActiveFirmware + ".0"
        return_dict["inactive_firmware"] = InactiveFirmware + ".0"
        return return_dict

    def decommission_all_datapaths(self):
        '''
        Return True if all datapaths are successfully de-commissioned, False otherwise
        '''
        # De-init all datapaths
        self.set_datapath_deinit((1 << self.NUM_CHANNELS) - 1)
        DELAY_RETRY_SEC = 0.1
        DELAY_MSEC = 1000
        for lane in range(self.NUM_CHANNELS):
            name = "DP{}State".format(lane + 1)
            if not self.wait_time_condition(lambda: (self.get_datapath_state())[name], 'DataPathDeactivated', DELAY_MSEC, DELAY_RETRY_SEC):
                return False

        for lane in range(self.NUM_CHANNELS):
            name = "ConfigStatusLane{}".format(lane + 1)
            if not self.wait_time_condition(lambda: (self.get_config_datapath_hostlane_status())[name], 'ConfigUndefined', DELAY_MSEC, DELAY_RETRY_SEC):
                return False

        # Decommission all lanes by applying AppSel=0
        self.set_application(((1 << self.NUM_CHANNELS) - 1), 0, 0)
        # Start with AppSel=0 i.e., undo any default AppSel
        self.scs_apply_datapath_init((1 << self.NUM_CHANNELS) - 1)
        for lane in range(self.NUM_CHANNELS):
            name = "ConfigStatusLane{}".format(lane + 1)
            if not self.wait_time_condition(lambda: (self.get_config_datapath_hostlane_status())[name], 'ConfigSuccess', DELAY_MSEC, DELAY_RETRY_SEC):
                return False

        return True
