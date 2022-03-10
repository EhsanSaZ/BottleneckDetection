try :
    from collectors.system_metric_collector import SystemMetricCollector
    from collectors.buffer_value_stat_collector import BufferValueStatCollector
    from collectors.disk_statistics_log_collector import DiskStatisticsLogCollector
except ModuleNotFoundError:
    from .collectors.buffer_value_stat_collector import BufferValueStatCollector
    from .collectors.system_metric_collector import SystemMetricCollector
    from .collectors.disk_statistics_log_collector import DiskStatisticsLogCollector


class StatisticsLogCollector:
    def __init__(self, disk_drive_name, sector_conversion_fctr=2):
        self.collect_system_metrics_obj = SystemMetricCollector()
        self.buffer_value_stat_collector_obj = BufferValueStatCollector()
        self.disk_statistics_log_collector_obj = DiskStatisticsLogCollector(disk_drive_name, sector_conversion_fctr=sector_conversion_fctr)

    def collect_system_metrics(self, pid_str, target_process):
        return self.collect_system_metrics_obj.collect_system_metrics(pid_str, target_process)

    def get_buffer_value(self):
        return self.buffer_value_stat_collector_obj.get_buffer_value()

    def get_disk_statistics_log_str(self):
        return self.disk_statistics_log_collector_obj.get_log_str()
