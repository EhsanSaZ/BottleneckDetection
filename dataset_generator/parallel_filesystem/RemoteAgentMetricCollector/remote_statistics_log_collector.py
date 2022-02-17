from utilities.remote_buffer_value_stat_collector import RemoteBufferValueStatCollector
from utilities.remote_system_metric_collector import RemoteSystemMetricCollector


class RemoteStatisticsLogCollector:
    def __init__(self):
        self.remote_collect_system_metrics_obj = RemoteSystemMetricCollector()
        self.remote_buffer_value_stat_collector_obj = RemoteBufferValueStatCollector()

    def remote_collect_system_metrics(self, pid_str, target_process):
        return self.remote_collect_system_metrics_obj.remote_collect_system_metrics(pid_str, target_process)

    def remote_get_buffer_value(self):
        return self.remote_buffer_value_stat_collector_obj.remote_get_buffer_value()
