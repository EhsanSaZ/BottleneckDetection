from utilities.remote_buffer_value_stat_collector import RemoteBufferValueStatCollector
from utilities.remote_system_metric_collector import RemoteSystemMetricCollector
from utilities.remote_file_osc_path_info import RemoteFileOscPathInfo
from utilities.remote_file_mdc_path_info import RemoteFileMdcPathInfo
from utilities.remote_client_ost_stat_collector import RemoteClientProcessOstStat
from utilities.remote_client_mdt_stat_collector import RemoteClientGetMdtStat

class RemoteStatisticsLogCollector:
    def __init__(self):
        self.remote_collect_system_metrics_obj = RemoteSystemMetricCollector()
        self.remote_buffer_value_stat_collector_obj = RemoteBufferValueStatCollector()
        self.remote_file_osc_path_info_obj = RemoteFileOscPathInfo()
        self.remote_file_mdc_path_info_obj = RemoteFileMdcPathInfo()
        self.remote_process_ost_stat_obj = RemoteClientProcessOstStat()
        self.remote_get_mdt_stat_obj = RemoteClientGetMdtStat()

    def remote_collect_system_metrics(self, pid_str, target_process):
        return self.remote_collect_system_metrics_obj.remote_collect_system_metrics(pid_str, target_process)

    def remote_get_buffer_value(self):
        return self.remote_buffer_value_stat_collector_obj.remote_get_buffer_value()

    def remote_collect_file_ost_path_info(self, pid, src_path):
        return self.remote_file_osc_path_info_obj.collect_file_ost_path_info(pid, src_path)
    
    def remote_collect_file_mdt_path_info(self,  pid, src_path):
        return self.remote_file_mdc_path_info_obj.collect_file_mdt_path_info(pid, src_path)

    def remote_process_ost_stat(self, ost_path, ost_dir_name, ost_stat_so_far=None):
        return self.remote_process_ost_stat_obj.remote_process_ost_stat(ost_path, ost_dir_name, ost_stat_so_far=None)
    
    def remote_get_mdt_stat(self, mdt_parent_path, mdt_dir_name, mdt_stat_so_far_dict=None):
        return self.remote_get_mdt_stat_obj.remote_get_mdt_stat(mdt_parent_path, mdt_dir_name, mdt_stat_so_far_dict)
