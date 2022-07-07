import threading
import time

import psutil

from AgentMetricCollector.statistics_log_collector import StatisticsLogCollector
import global_vars


class globalMetricsMonitor(threading.Thread):
    def __init__(self, sleep_time):
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.statics_collector = StatisticsLogCollector()

    def run(self):
        # global global_vars.system_buffer_value, global_vars.system_cpu_usage, global_vars.system_memory_usage
        while True:
            global_vars.system_cpu_usage = psutil.cpu_percent()
            global_vars.system_memory_usage = psutil.virtual_memory().percent
            global_vars.system_buffer_value = self.statics_collector.get_buffer_value()
            time.sleep(self.sleep_time)


class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, label_value, file_path_prefix):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.label_value = label_value
        self.file_path_prefix = file_path_prefix
    def run(self):
        output_file = open(self.file_path_prefix + str(self.label_value) + ".csv", "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


class overheadFileWriteThread(threading.Thread):
    def __init__(self, overhead_string, file_path):
        threading.Thread.__init__(self)
        self.overhead_string = overhead_string
        self.file_path = file_path

    def run(self):
        output_file = open(self.file_path, "a+")
        output_file.write(str(self.overhead_string))
        output_file.flush()
        output_file.close()
