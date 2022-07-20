try:
    from collectors.buffer_value_stat_collector import BufferValueStatCollector
    from collectors.system_metric_collector import SystemMetricCollector
    from collectors.file_osc_path_info import FileOscPathInfo
    from collectors.file_mdc_path_info import FileMdcPathInfo
    from collectors.client_ost_stat_collector import ClientProcessOstStat
    from collectors.client_mdt_stat_collector import ClientGetMdtStat
    from collectors.lustre_ost_stat_collector import LustreOstStatCollector
    from collectors.network_statistics_log_collector_ss_v2 import NetworkStatisticsLogCollectorSS_V2
except ModuleNotFoundError:
    from .collectors.buffer_value_stat_collector import BufferValueStatCollector
    from .collectors.system_metric_collector import SystemMetricCollector
    from .collectors.file_osc_path_info import FileOscPathInfo
    from .collectors.file_mdc_path_info import FileMdcPathInfo
    from .collectors.client_ost_stat_collector import ClientProcessOstStat
    from .collectors.client_mdt_stat_collector import ClientGetMdtStat
    from .collectors.lustre_ost_stat_collector import LustreOstStatCollector
    from .collectors.network_statistics_log_collector_ss_v2 import NetworkStatisticsLogCollectorSS_V2


class StatisticsLogCollector:
    def __init__(self, source_ip, source_port, destination_ip, destination_port, prefix=""):
        self.network_statistics_collector = NetworkStatisticsLogCollectorSS_V2(source_ip, source_port, destination_ip,
                                                                               destination_port, prefix)
        self.collect_system_metrics_obj = SystemMetricCollector(prefix)
        self.buffer_value_stat_collector_obj = BufferValueStatCollector(prefix)
        self.file_osc_path_info_obj = FileOscPathInfo()
        self.file_mdc_path_info_obj = FileMdcPathInfo()
        self.process_ost_stat_obj = ClientProcessOstStat(prefix)
        self.get_mdt_stat_obj = ClientGetMdtStat(prefix)
        self.lustre_ost_stat_collector_obj = LustreOstStatCollector()

    def collect_network_metrics(self):
        self.network_statistics_collector.collect_metrics()
        return self.network_statistics_collector.get_metrics_list()
    
    def collect_system_metrics(self, pid_str, target_process):
        self.collect_system_metrics_obj.collect_metrics(pid_str, target_process)
        return self.collect_system_metrics_obj.get_metrics_list()

    def get_buffer_value(self):
        self.buffer_value_stat_collector_obj.collect_metrics()
        return self.buffer_value_stat_collector_obj.get_metrics_list()

    def collect_file_ost_path_info(self, pid, src_path):
        return self.file_osc_path_info_obj.collect_file_ost_path_info(pid, src_path)

    def collect_file_mdt_path_info(self, pid, src_path):
        return self.file_mdc_path_info_obj.collect_file_mdt_path_info(pid, src_path)

    def process_ost_stat(self, ost_path, ost_dir_name):
        self.process_ost_stat_obj.collect_metrics(ost_path, ost_dir_name)
        return self.process_ost_stat_obj.get_metrics_list()

    def get_mdt_stat(self, mdt_parent_path, mdt_dir_name):
        self.get_mdt_stat_obj.collect_metrics(mdt_parent_path, mdt_dir_name)
        return self.get_mdt_stat_obj.get_metrics_list()

    def process_lustre_ost_stats(self, ost_agent_address, remote_ost_dir_name):
        self.lustre_ost_stat_collector_obj.collect_metrics(ost_agent_address, remote_ost_dir_name)
        return self.lustre_ost_stat_collector_obj.get_metrics_list()
