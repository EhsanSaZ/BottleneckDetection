import traceback
from subprocess import Popen, PIPE
import psutil
from google.protobuf.json_format import ParseDict, MessageToDict

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import SystemMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import SystemMetrics

class SystemMetricCollector(AbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {1: 'string', 2: 'string', 3: 'string', 4: 'string', 5: 'string', 6: 'string',
                                  7: 'string', 8: 'string', 9: 'string', 10: 'string', 11: 'string', 12: 'string',
                                  13: 'string', 14: 'string', 15: 'string', 16: 'string', 17: 'string', 18: 'string',
                                  19: 'string', 20: 'string', 21: 'string', 22: 'string', 23: 'string', 24: 'string',
                                  25: 'string', 26: 'string', 27: 'string', 28: 'string', 29: 'string', 30: 'intonly',
                                  31: 'intonly', 32: 'intonly', 33: 'intonly', 34: 'string', 35: 'string', 36: 'string',
                                  37: 'string', 38: 'string', 39: 'string', 40: 'string', 41: 'string', 42: 'string',
                                  43: 'string', 44: 'string', 45: 'string', 46: 'string', 47: 'string', 48: 'string',
                                  49: 'string', 50: 'string', 51: 'string', 52: 'string', 53: 'string', 54: 'string',
                                  55: 'string', 56: 'string', 57: 'string', 58: 'string', 59: 'string'}
        self.metrics_id_to_attr = {1: 'rchar', 2: 'wchar', 3: 'syscr', 4: 'syscw', 5: 'read_bytes_io',
                                   6: 'write_bytes_io', 7: 'cancelled_write_bytes', 8: 'pid', 9: 'ppid', 10: 'pgrp',
                                   11: 'session', 12: 'tty_nr', 13: 'tpgid', 14: 'flags', 15: 'minflt', 16: 'cminflt',
                                   17: 'majflt', 18: 'cmajflt', 19: 'utime', 20: 'stime', 21: 'cutime', 22: 'cstime',
                                   23: 'priority', 24: 'nice', 25: 'num_threads', 26: 'itrealvalue', 27: 'starttime',
                                   28: 'vsize', 29: 'rss', 30: 'rsslim', 31: 'startcode', 32: 'endcode',
                                   33: 'startstack', 34: 'kstkesp', 35: 'kstkeip', 36: 'signal', 37: 'blocked',
                                   38: 'sigignore', 39: 'sigcatch', 40: 'wchan', 41: 'nswap', 42: 'cnswap',
                                   43: 'exit_signal', 44: 'processor', 45: 'rt_priority', 46: 'policy',
                                   47: 'delayacct_blkio_ticks', 48: 'guest_time', 49: 'cguest_time', 50: 'start_data',
                                   51: 'end_data', 52: 'start_brk', 53: 'arg_start', 54: 'arg_end', 55: 'env_start',
                                   56: 'env_end', 57: 'exit_code', 58: 'cpu_usage_percentage',
                                   59: 'mem_usage_percentage'}
        self.seperator_string = '--result--'

    def collect_metrics(self, pid_str, target_process):
        self.collect_system_metrics(pid_str, target_process)

    def collect_system_metrics(self, pid_str, target_process):
        # pid = int(pid_str.strip())
        cmd = "cat /proc/{pid}/io; echo {seperator}; cat /proc/{pid}/stat".format(pid=pid_str.strip(), seperator=self.seperator_string)

        value_list = []
        # create process to collect io and stat metrics
        try:
            proc = Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split(self.seperator_string)
            io_output_parts = res_parts[0].split("\n")
            for line in io_output_parts:
                if len(line.strip()) > 0:
                    index = line.rfind(":")
                    value = int(line[index + 1:].strip())
                    value_list.append(value)
            stat_output_part = res_parts[1].split(" ")
            for line in stat_output_part:
                if len(line.strip()) > 0:
                    try:
                        value = int(line.strip())
                        value_list.append(value)
                    except:
                        # only convert numbers to int as pass error for other strings
                        pass
                        # traceback.print_exc()
            # proc = Popen(['cat', '/proc/' + str(pid).strip() + '/io'], universal_newlines=True, stdout=PIPE)
            # res = proc.communicate()[0]
            # res_parts = res.split("\n")
            # for line in res_parts:
            #     if len(line.strip()) > 0:
            #         index = line.rfind(":")
            #         value = int(line[index + 1:].strip())
            #         value_list.append(value)
        except:
            print("io / stat  not possible")
            traceback.print_exc()

        # create process to collect cpu memory metrics
        try:
            value_list.append(float(target_process.cpu_percent()))
            value_list.append(float(target_process.memory_percent()))
            # proc = Popen(['ps', '-p', str(pid).strip(), '-o', '%cpu,%mem'], universal_newlines=True, stdout=PIPE)
            # res = proc.communicate()[0]
            # res_parts = res.split("\n")
            # for line in res_parts:
            #     if len(line.strip()) > 0:
            #         if "%CPU" not in line:
            #             parts = line.split(" ")
            #             for x in parts:
            #                 if len(x.strip()) > 0:
            #                     value_list.append(float(x))
        except psutil.NoSuchProcess as e:
            raise e
        except:
            traceback.print_exc()
            print("cpu mem is not possible")
        self.metrics_list = value_list
        self.metrics_list_to_str()
        self.metrics_list_to_dict()
        # return value_list

    def metrics_list_to_str(self):
        output_string = ""
        for item in self.metrics_list:
            output_string += "," + str(item)
        if output_string.startswith(","):
            output_string = output_string[1:]
        self.metrics_str = output_string

    def metrics_list_to_dict(self):
        tmp_dict = {}
        keys_list = list(self.metrics_id_to_attr.keys())
        for index in range(len(self.metrics_list)):
            type_ = self.metrics_datatypes[keys_list[index]]
            tmp_dict["{}{}".format(self.prefix, self.metrics_id_to_attr[keys_list[index]])] = self._get_data_type(
                self.metrics_list[index], type_)
        self.metrics_dict = tmp_dict

    def get_metrics_list_to_dict_no_prefix(self):
        metrics_dict_no_prefix = {}
        keys_list = list(self.metrics_id_to_attr.keys())
        for index in range(len(self.metrics_list)):
            type_ = self.metrics_datatypes[keys_list[index]]
            metrics_dict_no_prefix[self.metrics_id_to_attr[keys_list[index]]] = self._get_data_type(
                self.metrics_list[index], type_)
        return metrics_dict_no_prefix

    def get_proto_message(self):
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), SystemMetrics())
        return message
