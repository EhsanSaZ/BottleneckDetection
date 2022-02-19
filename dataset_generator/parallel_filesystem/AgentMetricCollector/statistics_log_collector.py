try :
    from collectors.buffer_value_stat_collector import BufferValueStatCollector
    from collectors.system_metric_collector import SystemMetricCollector
    from collectors.file_osc_path_info import FileOscPathInfo
    from collectors.file_mdc_path_info import FileMdcPathInfo
    from collectors.client_ost_stat_collector import ClientProcessOstStat
    from collectors.client_mdt_stat_collector import ClientGetMdtStat
    from collectors.lustre_ost_stat_collector import LustreOstStatCollector
except ModuleNotFoundError:
    from .collectors.buffer_value_stat_collector import BufferValueStatCollector
    from .collectors.system_metric_collector import SystemMetricCollector
    from .collectors.file_osc_path_info import FileOscPathInfo
    from .collectors.file_mdc_path_info import FileMdcPathInfo
    from .collectors.client_ost_stat_collector import ClientProcessOstStat
    from .collectors.client_mdt_stat_collector import ClientGetMdtStat
    from .collectors.lustre_ost_stat_collector import LustreOstStatCollector


class StatisticsLogCollector:
    def __init__(self):
        self.collect_system_metrics_obj = SystemMetricCollector()
        self.buffer_value_stat_collector_obj = BufferValueStatCollector()
        self.file_osc_path_info_obj = FileOscPathInfo()
        self.file_mdc_path_info_obj = FileMdcPathInfo()
        self.process_ost_stat_obj = ClientProcessOstStat()
        self.get_mdt_stat_obj = ClientGetMdtStat()
        self.lustre_ost_stat_collector_obj = LustreOstStatCollector()

    def collect_system_metrics(self, pid_str, target_process):
        return self.collect_system_metrics_obj.collect_system_metrics(pid_str, target_process)

    def get_buffer_value(self):
        return self.buffer_value_stat_collector_obj.get_buffer_value()

    def collect_file_ost_path_info(self, pid, src_path):
        return self.file_osc_path_info_obj.collect_file_ost_path_info(pid, src_path)
    
    def collect_file_mdt_path_info(self, pid, src_path):
        return self.file_mdc_path_info_obj.collect_file_mdt_path_info(pid, src_path)

    def process_ost_stat(self, ost_path, ost_dir_name, ost_stat_so_far=None):
        return self.process_ost_stat_obj.process_ost_stat(ost_path, ost_dir_name, ost_stat_so_far=None)
    
    def get_mdt_stat(self, mdt_parent_path, mdt_dir_name, mdt_stat_so_far_dict=None):
        return self.get_mdt_stat_obj.get_mdt_stat(mdt_parent_path, mdt_dir_name, mdt_stat_so_far_dict)

    def process_lustre_ost_stats(self, st_agent_address, remote_ost_dir_name, remote_ost_stats_so_far=None):
        self.lustre_ost_stat_collector_obj.process_lustre_ost_stats(st_agent_address, remote_ost_dir_name, remote_ost_stats_so_far)
