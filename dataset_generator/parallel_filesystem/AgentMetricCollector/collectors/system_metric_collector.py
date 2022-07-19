import json
import traceback
from subprocess import Popen, PIPE
import psutil

try:
    from basic_abstract_collector import BasicAbstractCollector
except ModuleNotFoundError:
    from .basic_abstract_collector import BasicAbstractCollector


class SystemMetricCollector(BasicAbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {30: 'string', 31: 'string', 32: 'string', 33: 'string', 34: 'string', 35: 'string',
                                  36: 'string', 37: 'string', 38: 'string', 39: 'string', 40: 'string', 41: 'string',
                                  42: 'string', 43: 'string', 44: 'string', 45: 'string', 46: 'string', 47: 'string',
                                  48: 'string', 49: 'string', 50: 'string', 51: 'string', 52: 'string', 53: 'string',
                                  54: 'string', 55: 'string', 56: 'string', 57: 'string', 58: 'string', 59: 'intonly',
                                  60: 'intonly', 61: 'intonly', 62: 'intonly', 63: 'string', 64: 'string', 65: 'string',
                                  66: 'string', 67: 'string', 68: 'string', 69: 'string', 70: 'string', 71: 'string',
                                  72: 'string', 73: 'string', 74: 'string', 75: 'string', 76: 'string', 77: 'string',
                                  78: 'string', 79: 'string', 80: 'string', 81: 'string', 82: 'string', 83: 'string',
                                  84: 'string', 85: 'string', 86: 'string'}
        self.metrics_id_to_attr = {30: 'rchar', 31: 'wchar', 32: 'syscr', 33: 'syscw', 34: 'read_bytes_io',
                                   35: 'write_bytes_io', 36: 'cancelled_write_bytes', 37: 'pid', 38: 'ppid', 39: 'pgrp',
                                   40: 'session', 41: 'tty_nr', 42: 'tpgid', 43: 'flags', 44: 'minflt', 45: 'cminflt',
                                   46: 'majflt', 47: 'cmajflt', 48: 'utime', 49: 'stime', 50: 'cutime', 51: 'cstime',
                                   52: 'priority', 53: 'nice', 54: 'num_threads', 55: 'itrealvalue', 56: 'starttime',
                                   57: 'vsize', 58: 'rss', 59: 'rsslim', 60: 'startcode', 61: 'endcode',
                                   62: 'startstack', 63: 'kstkesp', 64: 'kstkeip', 65: 'signal', 66: 'blocked',
                                   67: 'sigignore', 68: 'sigcatch', 69: 'wchan', 70: 'nswap', 71: 'cnswap',
                                   72: 'exit_signal', 73: 'processor', 74: 'rt_priority', 75: 'policy',
                                   76: 'delayacct_blkio_ticks', 77: 'guest_time', 78: 'cguest_time', 79: 'start_data',
                                   80: 'end_data', 81: 'start_brk', 82: 'arg_start', 83: 'arg_end', 84: 'env_start',
                                   85: 'env_end', 86: 'exit_code'}

    def collect_system_metrics(self, pid_str, target_process):
        pid = int(pid_str.strip())

        value_list = []
        # create process to collect io metrics
        try:
            proc = Popen(['cat', '/proc/' + str(pid).strip() + '/io'], universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split("\n")
            for line in res_parts:
                if len(line.strip()) > 0:
                    index = line.rfind(":")
                    value = int(line[index + 1:].strip())
                    value_list.append(value)
        except:
            print("io stat not possible")
            traceback.print_exc()

        # create process to collect stat metrics
        try:
            proc = Popen(['cat', '/proc/' + str(pid).strip() + '/stat'], universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split(" ")
            for line in res_parts:
                if len(line.strip()) > 0:
                    try:
                        value = int(line.strip())
                        value_list.append(value)
                    except:
                        # only convert numbers to int as pass error for other strings
                        pass
                        # traceback.print_exc()
        except:
            print("stat not possible")
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
        for index, key in enumerate(self.metrics_datatypes.keys()):
            type_ = self.metrics_datatypes[key]
            tmp_dict["{}{}".format(self.prefix, self.metrics_id_to_attr[key])] = self._get_data_type(
                self.metrics_list[index], type_)
        self.metrics_dict = tmp_dict

    def get_metrics_name_list(self):
        return list(self.metrics_id_to_attr.values())
    
    def get_metrics_str(self):
        return self.metrics_str

    def get_metrics_list(self):
        return self.metrics_list

    def get_metrics_dict(self):
        return self.metrics_dict

    def get_metrics_json_str(self):
        return json.dumps(self.get_metrics_dict())
