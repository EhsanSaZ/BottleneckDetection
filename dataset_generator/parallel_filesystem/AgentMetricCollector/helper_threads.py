import threading
import time

import psutil

from collectors.buffer_value_stat_collector import BufferValueStatCollector
from collectors.resource_usage_collector import ResourceUsageCollector
# import system_monitoring_global_vars
from multiprocessing import Process

class globalMetricsMonitor(Process):
    def __init__(self, sleep_time, system_cpu_mem_usage_list, system_cpu_mem_usage_dict,
                 system_buffer_value_list, system_buffer_value_dict, **kwargs):
        super(globalMetricsMonitor, self).__init__(**kwargs)
        self.sleep_time = sleep_time
        self.resource_usage_collector = ResourceUsageCollector()
        self.buffer_value_collector = BufferValueStatCollector()
        self.system_cpu_mem_usage_list = system_cpu_mem_usage_list
        self.system_cpu_mem_usage_dict = system_cpu_mem_usage_dict
        self.system_buffer_value_list = system_buffer_value_list
        self.system_buffer_value_dict = system_buffer_value_dict

    def run(self):
        # global system_monitoring_global_vars.system_buffer_value, system_monitoring_global_vars.system_cpu_usage, system_monitoring_global_vars.system_memory_usage
        while True:
            self.resource_usage_collector.collect_metrics()
            # system_monitoring_global_vars.system_cpu_mem_usage = self.resource_usage_collector.get_metrics_list()
            self.system_cpu_mem_usage_list[0] = float(self.resource_usage_collector.get_metrics_list()[0])
            self.system_cpu_mem_usage_list[1] = float(self.resource_usage_collector.get_metrics_list()[1])
            # system_monitoring_global_vars.system_cpu_mem_usage_dict = self.resource_usage_collector.get_metrics_dict()
            self.system_cpu_mem_usage_dict["system_cpu_percent"] = self.resource_usage_collector.get_metrics_dict()["system_cpu_percent"]
            self.system_cpu_mem_usage_dict["system_memory_percent"] = self.resource_usage_collector.get_metrics_dict()["system_memory_percent"]
            # # system_monitoring_global_vars.system_cpu_mem_usage_proto_message.CopyFrom(self.resource_usage_collector.get_proto_message())
            # # system_monitoring_global_vars.system_cpu_usage = self.resource_usage_collector.get_metrics_list()[0]
            # # system_monitoring_global_vars.system_memory_usage = self.resource_usage_collector.get_metrics_list()[1]
            self.buffer_value_collector.collect_metrics()
            # system_monitoring_global_vars.system_buffer_value = self.buffer_value_collector.get_metrics_list()
            self.system_buffer_value_list[0] = int(self.buffer_value_collector.get_metrics_list()[0])
            self.system_buffer_value_list[1] = int(self.buffer_value_collector.get_metrics_list()[1])
            self.system_buffer_value_list[2] = int(self.buffer_value_collector.get_metrics_list()[2])
            self.system_buffer_value_list[3] = int(self.buffer_value_collector.get_metrics_list()[3])
            self.system_buffer_value_list[4] = int(self.buffer_value_collector.get_metrics_list()[4])
            self.system_buffer_value_list[5] = int(self.buffer_value_collector.get_metrics_list()[5])

            self.system_buffer_value_dict["tcp_rcv_buffer_min"] = self.buffer_value_collector.get_metrics_dict()["tcp_rcv_buffer_min"]
            self.system_buffer_value_dict["tcp_rcv_buffer_default"] = self.buffer_value_collector.get_metrics_dict()["tcp_rcv_buffer_default"]
            self.system_buffer_value_dict["tcp_rcv_buffer_max"] = self.buffer_value_collector.get_metrics_dict()["tcp_rcv_buffer_max"]
            self.system_buffer_value_dict["tcp_snd_buffer_min"] = self.buffer_value_collector.get_metrics_dict()["tcp_snd_buffer_min"]
            self.system_buffer_value_dict["tcp_snd_buffer_default"] = self.buffer_value_collector.get_metrics_dict()["tcp_snd_buffer_default"]
            self.system_buffer_value_dict["tcp_snd_buffer_max"] = self.buffer_value_collector.get_metrics_dict()["tcp_snd_buffer_max"]
            #
            # system_monitoring_global_vars.system_buffer_value_dict = self.buffer_value_collector.get_metrics_dict()
            # system_monitoring_global_vars.system_buffer_value_proto_message.CopyFrom(self.buffer_value_collector.get_proto_message())
            time.sleep(self.sleep_time)


class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, file_path_prefix, label_value):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.label_value = label_value
        self.file_path_prefix = file_path_prefix

    def run(self):
        output_file = open("{}{}.csv".format(self.file_path_prefix, str(self.label_value)), "a+")
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
