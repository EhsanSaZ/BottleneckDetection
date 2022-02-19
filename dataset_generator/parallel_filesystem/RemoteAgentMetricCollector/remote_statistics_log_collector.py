from collectors.remote_buffer_value_stat_collector import RemoteBufferValueStatCollector
from collectors.remote_system_metric_collector import RemoteSystemMetricCollector
from collectors.remote_file_osc_path_info import RemoteFileOscPathInfo
from collectors.remote_file_mdc_path_info import RemoteFileMdcPathInfo
from collectors.remote_client_ost_stat_collector import RemoteClientProcessOstStat
from collectors.remote_client_mdt_stat_collector import RemoteClientGetMdtStat
from collectors.remote_lustre_ost_stat_collector import RemoteLustreOstStatCollector


class RemoteStatisticsLogCollector:
    def __init__(self):
        self.remote_collect_system_metrics_obj = RemoteSystemMetricCollector()
        self.remote_buffer_value_stat_collector_obj = RemoteBufferValueStatCollector()
        self.remote_file_osc_path_info_obj = RemoteFileOscPathInfo()
        self.remote_file_mdc_path_info_obj = RemoteFileMdcPathInfo()
        self.remote_process_ost_stat_obj = RemoteClientProcessOstStat()
        self.remote_get_mdt_stat_obj = RemoteClientGetMdtStat()
        self.remote_lustre_ost_stat_collector_obj = RemoteLustreOstStatCollector()

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

    def process_remote_lustre_ost_stats(self, st_agent_address, remote_ost_dir_name, remote_ost_stats_so_far=None):
        self.remote_lustre_ost_stat_collector_obj.process_remote_lustre_ost_stats(st_agent_address, remote_ost_dir_name, remote_ost_stats_so_far)
