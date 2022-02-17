from utilities.remote_buffer_value_stat_collector import RemoteBufferValueStatCollector


class RemoteStatisticsLogCollector:
    def __init__(self):
        self.remote_buffer_value_stat_collector_obj = RemoteBufferValueStatCollector()

    def remote_get_buffer_value(self):
        return self.remote_buffer_value_stat_collector_obj.remote_get_buffer_value()

