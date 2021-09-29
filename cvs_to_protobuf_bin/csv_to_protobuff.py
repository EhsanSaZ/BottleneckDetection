from dataset_generator import bottleneck_pb2
import csv
import os
import glob
import pandas as pd
import re

from pathlib import Path

class CSV_to_Proto:
    def __init__(self, folder_dir, serialize_file="0"):
        self.serialize_file = serialize_file
        self.folder_name = folder_dir
        self.binary_dir = "./binary_logs"
        Path(self.binary_dir).mkdir(parents=True, exist_ok=True)
        self.network_type = {"DTNS": 0, "AWS": 1, "CC": 2, "AWS_FXS": 3, "UNDEFINED": 4}
        self.environment = "UNDEFINED" if self.folder_name.split("/")[2].upper() not in self.network_type else self.folder_name.split("/")[2]
        self.file_system = "normal" if "FXS" not in self.environment else "lustre"
        self.bottleneck_logs = self.check_serialize_file(self.serialize_file)
        self.id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate', 4: 'avg_retransmission_timeout_value',
                           5: 'byte_ack', 6: 'seg_out', 7: 'retrans', 8: 'mss_value', 9: 'ssthresh_value',
                           10: 'segs_in', 11: 'avg_send_value', 12: 'unacked_value', 13: 'rcv_space',
                           14: 'send_buffer_value', 15: 'read_req', 16: 'write_req', 17: 'rkB', 18: 'wkB', 19: 'rrqm',
                           20: 'wrqm', 21: 'rrqm_perc', 22: 'wrqm_perc', 23: 'r_await', 24: 'w_await', 25: 'aqu_sz',
                           26: 'rareq_sz', 27: 'wareq_sz', 28: 'svctm', 29: 'util', 30: 'rchar', 31: 'wchar',
                           32: 'syscr', 33: 'syscw', 34: 'read_bytes_io', 35: 'write_bytes_io',
                           36: 'cancelled_write_bytes', 37: 'pid', 38: 'ppid', 39: 'pgrp', 40: 'session', 41: 'tty_nr',
                           42: 'tpgid', 43: 'flags', 44: 'minflt', 45: 'cminflt', 46: 'majflt', 47: 'cmajflt',
                           48: 'utime', 49: 'stime', 50: 'cutime', 51: 'cstime', 52: 'priority', 53: 'nice',
                           54: 'num_threads', 55: 'itrealvalue', 56: 'starttime', 57: 'vsize', 58: 'rss', 59: 'rsslim',
                           60: 'startcode', 61: 'endcode', 62: 'startstack', 63: 'kstkesp', 64: 'kstkeip', 65: 'signal',
                           66: 'blocked', 67: 'sigignore', 68: 'sigcatch', 69: 'wchan', 70: 'nswap', 71: 'cnswap',
                           72: 'exit_signal', 73: 'processor', 74: 'rt_priority', 75: 'policy',
                           76: 'delayacct_blkio_ticks', 77: 'guest_time', 78: 'cguest_time', 79: 'start_data',
                           80: 'end_data', 81: 'start_brk', 82: 'arg_start', 83: 'arg_end', 84: 'env_start',
                           85: 'env_end', 86: 'exit_code', 87: 'cpu_usage_percentage', 88: 'mem_usage_percentage',
                           89: 'tcp_rcv_buffer_min', 90: 'tcp_rcv_buffer_default', 91: 'tcp_rcv_buffer_max',
                           92: 'tcp_snd_buffer_min', 93: 'tcp_snd_buffer_default', 94: 'tcp_snd_buffer_max',
                           95: 'req_waittime', 96: 'req_active', 97: 'read_bytes', 98: 'write_bytes', 99: 'ost_setattr',
                           100: 'ost_read', 101: 'ost_write', 102: 'ost_get_info', 103: 'ost_connect', 104: 'ost_punch',
                           105: 'ost_statfs', 106: 'ost_sync', 107: 'ost_quotactl', 108: 'ldlm_cancel', 109: 'obd_ping',
                           110: 'pending_read_pages', 111: 'read_RPCs_in_flight', 112: 'avg_waittime_md1',
                           113: 'inflight_md1', 114: 'unregistering_md1', 115: 'timeouts_md1', 116: 'req_waittime_md1',
                           117: 'req_active_md1', 118: 'mds_getattr_md1', 119: 'mds_getattr_lock_md1',
                           120: 'mds_close_md1', 121: 'mds_readpage_md1', 122: 'mds_connect_md1',
                           123: 'mds_get_root_md1', 124: 'mds_statfs_md1', 125: 'mds_sync_md1', 126: 'mds_quotactl_md1',
                           127: 'mds_getxattr_md1', 128: 'mds_hsm_state_set_md1', 129: 'ldlm_cancel_md1',
                           130: 'obd_ping_md1', 131: 'seq_query_md1', 132: 'fld_query_md1', 133: 'close_md1',
                           134: 'create_md1', 135: 'enqueue_md1', 136: 'getattr_md1', 137: 'intent_lock_md1',
                           138: 'link_md1', 139: 'rename_md1', 140: 'setattr_md1', 141: 'fsync_md1',
                           142: 'read_page_md1', 143: 'unlink_md1', 144: 'setxattr_md1', 145: 'getxattr_md1',
                           146: 'intent_getattr_async_md1', 147: 'revalidate_lock_md1', 148: 'avg_waittime_md2',
                           149: 'inflight_md2', 150: 'unregistering_md2', 151: 'timeouts_md2', 152: 'req_waittime_md2',
                           153: 'req_active_md2', 154: 'mds_getattr_md2', 155: 'mds_close_md2', 156: 'mds_readpage_md2',
                           157: 'mds_connect_md2', 158: 'mds_statfs_md2', 159: 'mds_sync_md2', 160: 'mds_quotactl_md2',
                           161: 'mds_getxattr_md2', 162: 'mds_hsm_state_set_md2', 163: 'ldlm_cancel_md2',
                           164: 'obd_ping_md2', 165: 'seq_query_md2', 166: 'fld_query_md2', 167: 'close_md2',
                           168: 'create_md2', 169: 'enqueue_md2', 170: 'getattr_md2', 171: 'intent_lock_md2',
                           172: 'link_md2', 173: 'rename_md2', 174: 'setattr_md2', 175: 'fsync_md2',
                           176: 'read_page_md2', 177: 'unlink_md2', 178: 'setxattr_md2', 179: 'getxattr_md2',
                           180: 'intent_getattr_async_md2', 181: 'revalidate_lock_md2', 182: 'label_value'}
        self.attr_to_id = {}
        for i in self.id_to_attr:
            self.attr_to_id[self.id_to_attr[i]] = i
        self.datatypes = {1: 'float', 2: 'string', 3: 'float', 4: 'float', 5: 'float', 6: 'float', 7: 'float',
                          8: 'float', 9: 'float', 10: 'float', 11: 'string', 12: 'float', 13: 'float', 14: 'float',
                          15: 'float', 16: 'float', 17: 'float', 18: 'float', 19: 'float', 20: 'float', 21: 'float',
                          22: 'float', 23: 'float', 24: 'float', 25: 'float', 26: 'float', 27: 'float', 28: 'float',
                          29: 'float', 30: 'int', 31: 'int', 32: 'int', 33: 'int', 34: 'int', 35: 'int', 36: 'int',
                          37: 'int', 38: 'int', 39: 'int', 40: 'int', 41: 'int', 42: 'int', 43: 'int', 44: 'int',
                          45: 'int', 46: 'int', 47: 'int', 48: 'int', 49: 'int', 50: 'int', 51: 'int', 52: 'int',
                          53: 'int', 54: 'int', 55: 'int', 56: 'int', 57: 'int', 58: 'int',
                          59: 'intonly', 60: 'intonly', 61: 'intonly', 62: 'intonly', 63: 'int', 64: 'int', 65: 'int',
                          66: 'int', 67: 'int', 68: 'int', 69: 'int', 70: 'int', 71: 'int', 72: 'int', 73: 'int',
                          74: 'int', 75: 'int', 76: 'int', 77: 'int', 78: 'int', 79: 'int', 80: 'int', 81: 'int',
                          82: 'int', 83: 'int', 84: 'int', 85: 'int', 86: 'int', 87: 'float', 88: 'float', 89: 'int',
                          90: 'int', 91: 'int', 92: 'int', 93: 'int', 94: 'int', 95: 'int', 96: 'int', 97: 'int',
                          98: 'int', 99: 'int', 100: 'int', 101: 'int', 102: 'int', 103: 'int', 104: 'int', 105: 'int',
                          106: 'int', 107: 'int', 108: 'int', 109: 'int', 110: 'int', 111: 'int', 112: 'int',
                          113: 'int', 114: 'int', 115: 'int', 116: 'int', 117: 'int', 118: 'int', 119: 'int',
                          120: 'int', 121: 'int', 122: 'int', 123: 'int', 124: 'int', 125: 'int', 126: 'int',
                          127: 'int', 128: 'int', 129: 'int', 130: 'int', 131: 'int', 132: 'int', 133: 'int',
                          134: 'int', 135: 'int', 136: 'int', 137: 'int', 138: 'int', 139: 'int', 140: 'int',
                          141: 'int', 142: 'int', 143: 'int', 144: 'int', 145: 'int', 146: 'int', 147: 'int',
                          148: 'int', 149: 'int', 150: 'int', 151: 'int', 152: 'int', 153: 'int', 154: 'int',
                          155: 'int', 156: 'int', 157: 'int', 158: 'int', 159: 'int', 160: 'int', 161: 'int',
                          162: 'int', 163: 'int', 164: 'int', 165: 'int', 166: 'int', 167: 'int', 168: 'int',
                          169: 'int', 170: 'int', 171: 'int', 172: 'int', 173: 'int', 174: 'int', 175: 'int',
                          176: 'int', 177: 'int', 178: 'int', 179: 'int', 180: 'int', 181: 'int', 182: 'int'}
        self.filetype = {0: {}, 1: {'read_threads': 1}, 2: {'read_threads': 2}, 3: {'read_threads': 3},
                         4: {'read_threads': 4}, 5: {'read_threads': 5}, 6: {'read_threads': 6}, 7: {'read_threads': 7},
                         8: {'read_threads': 8}, 9: {'read_threads': 9}, 10: {'read_threads': 10},
                         11: {'read_threads': 11}, 12: {'read_threads': 12}, 13: {'read_threads': 13},
                         14: {'read_threads': 14}, 15: {'read_threads': 15}, 16: {'read_threads': 16},
                         17: {'write_threads': 4}, 18: {'write_threads': 8}, 19: {'write_threads': 12},
                         20: {'write_threads': 16}, 21: {'write_threads': 20}, 22: {'write_threads': 24},
                         23: {'write_threads': 28}, 24: {'write_threads': 32}, 25: {'write_threads': 36},
                         26: {'write_threads': 40}, 27: {'write_threads': 44}, 28: {'write_threads': 48},
                         29: {'write_threads': 64}, 30: {'write_threads': 72}, 31: {'write_threads': 96},
                         32: {'write_threads': 128}, 33: {'cpu_stress': 2}, 34: {'io_stress': 10},
                         35: {'mem_stress': 0.98}, 36: {'link_loss': 0.5}, 37: {'link_loss': 0.1},
                         38: {'link_loss': 0.05}, 39: {'link_loss': 1},
                         40: {'link_delay': 0.02, "link_delay_distribution": 0},
                         41: {'link_delay': 0.03, "link_delay_distribution": 0},
                         42: {'link_delay': 0.04, "link_delay_distribution": 0},
                         43: {'link_delay': 0.05, "link_delay_distribution": 0}, 44: {'link_duplicate': 0.5},
                         45: {'link_duplicate': 0.1}, 46: {'link_duplicate': 0.05}, 47: {'link_duplicate': 1},
                         48: {'link_corrupt': 0.5}, 49: {'link_corrupt': 0.1}, 50: {'link_corrupt': 0.05},
                         51: {'link_corrupt': 1}, 52: {'link_delay': 1.0, 'link_reorder': 0.5},
                         53: {'link_delay': 1.0, 'link_reorder': 0.1}, 54: {'link_delay': 1.0, 'link_reorder': 0.05},
                         55: {'link_delay': 1.0, 'link_reorder': 1}}
        self.protobuff_files = {}
        if self.file_system == "normal":
            self.keys = list(range(1, 95)) + [182]
        else:
            self.keys = list(range(1, 15)) + [44, 45, 46, 47, 48, 49, 50, 51, 54, 55, 57, 58, 59, 70, 71, 74, 76, 77,
                                              78] + list(range(87, 183))

    def read_csv(self, filename):
        data = []
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count = 0
            for row in csv_reader:
                if count == 0:
                    count += 1
                    continue
                new_row = []
                for i in range(len(row)):
                    type_ = self.datatypes[self.keys[i]]
                    new_row.append(self.get_data_type(row[i], type_))
                data.append(new_row)
        return data

    def get_data_type(self, val, type_):
        if type_ == "string":
            return float(self.get_mbps(val))
        elif type_ == "float":
            return float(val)
        elif type_ == "intonly":
            tmp_value = str(val).split(".")[0]
            return int(tmp_value)
        else:
            return int(float(val))

    def get_mbps(self, thpt):
        if self.is_number(thpt):
            return thpt
        thpts = thpt.split("Mb")
        if len(thpts) == 2:
            return float(thpts[0])
        thpts = thpt.split("Kb")
        if len(thpts) == 2:
            return float(thpts[0]) / 1000.
        thpts = thpt.split("b")
        if len(thpts) == 2:
            return float(thpts[0]) / (1000. * 1000.)
        thpts = thpt.split("MB")
        if len(thpts) == 2:
            return float(thpts[0]) * (1.024 * 1.024 * 8)
        thpts = thpt.split("KB")
        if len(thpts) == 2:
            return float(thpts[0]) * (1024 * 8) / (1000.)
        thpts = thpt.split("B")
        if len(thpts) == 2:
            return float(thpts[0]) * (8) / (1000. * 1000.)
        try:
            return float(thpt)
        except:
            return 0.0

    def get_file_id(self, filename):
        number_compile = re.compile('\d+')
        return int(number_compile.findall(filename.split("/")[-1])[0])

    def write_to_proto(self, filename):
        logs = self.read_csv(filename)
        this_file_logs = bottleneck_pb2.BottleneckFile()
        if self.file_system == "normal":
            id_ = self.get_file_id(filename)
            if id_ not in self.protobuff_files:
                self.protobuff_files[id_] = bottleneck_pb2.BottleneckFile()
            this_file_logs = self.protobuff_files[id_]
            attrs = self.filetype[id_]
            for i in attrs:
                this_file_logs.__setattr__(i, attrs[i])
        this_file_logs.__setattr__("network_type", self.network_type[self.environment.upper()])
        this_file_logs.__setattr__("created_time_utc", os.path.getctime(filename))

        length_log = 0 if len(logs) == 0 else len(logs[0])
        for log in logs:
            new_log = bottleneck_pb2.BottleneckLog()
            for i in range(len(self.keys)):
                new_log.__setattr__(self.id_to_attr[self.keys[i]], log[i])
            this_file_logs.rows.append(new_log)
        print("[+] The length of the rows is %d" % len(this_file_logs.rows))
        self.bottleneck_logs.logs.append(this_file_logs)

    def aws_write(self, main_list, headers):
        for file_ in main_list:
            this_file_logs = bottleneck_pb2.BottleneckFile()
            this_file_logs.__setattr__("network_type", self.network_type[self.environment.upper()])
            for log in main_list[file_]:
                new_log = bottleneck_pb2.BottleneckLog()
                for i in range(len(headers)):
                    new_log.__setattr__(headers[i], log[i])

                this_file_logs.rows.append(new_log)
            self.bottleneck_logs.logs.append(this_file_logs)

    def write_to_binary(self, serialize_file):
        try:
            file_path = self.binary_dir + "/" + self.environment + "/" + serialize_file
            Path(self.binary_dir + "/" + self.environment).mkdir(parents=True, exist_ok=True)
            f = open(file_path, "wb")
            f.write(self.bottleneck_logs.SerializeToString())
            f.close()
            print("Binary file of path: " + file_path + " is created.")
        except IOError:
            print("[+] Error while creating binary file.")

    def get_info_list(self, row):
        list_ = {0: 'avg_rtt_value', 1: 'pacing_rate', 2: 'cwnd_rate', 3: 'avg_retransmission_timeout_value',
                 4: 'byte_ack', 5: 'seg_out', 6: 'retrans', 7: 'mss_value', 8: 'ssthresh_value', 9: 'segs_in',
                 10: 'avg_send_value', 11: 'unacked_value', 12: 'rcv_space', 13: 'send_buffer_value', 14: 'rchar',
                 15: 'wchar', 16: 'syscr', 17: 'syscw', 18: 'read_bytes_io', 19: 'write_bytes_io',
                 20: 'cancelled_write_bytes', 21: 'pid', 22: 'ppid', 23: 'pgrp', 24: 'session', 25: 'tty_nr',
                 26: 'tpgid',
                 27: 'flags', 28: 'minflt', 29: 'cminflt', 30: 'majflt', 31: 'cmajflt', 32: 'utime', 33: 'stime',
                 34: 'cutime', 35: 'cstime', 36: 'priority', 37: 'nice', 38: 'num_threads', 39: 'itrealvalue',
                 40: 'starttime', 41: 'vsize', 42: 'rss', 43: 'rsslim', 44: 'startcode', 45: 'endcode',
                 46: 'startstack',
                 47: 'kstkesp', 48: 'kstkeip', 49: 'signal', 50: 'blocked', 51: 'sigignore', 52: 'sigcatch',
                 53: 'wchan',
                 54: 'nswap', 55: 'cnswap', 56: 'exit_signal', 57: 'processor', 58: 'rt_priority', 59: 'policy',
                 60: 'delayacct_blkio_ticks', 61: 'guest_time', 62: 'cguest_time', 63: 'start_data', 64: 'end_data',
                 65: 'start_brk', 66: 'arg_start', 67: 'arg_end', 68: 'env_start', 69: 'env_end', 70: 'exit_code',
                 71: 'cpu_usage_percentage', 72: 'mem_usage_percentage', 73: 'tcp_rcv_buffer_min',
                 74: 'tcp_rcv_buffer_default',
                 75: 'tcp_rcv_buffer_max', 76: 'tcp_snd_buffer_min', 77: 'tcp_snd_buffer_default',
                 78: 'tcp_snd_buffer_max'}

        first_list = ['req_waittime', 'req_active', 'read_bytes', 'write_bytes', 'ost_setattr', 'ost_read', 'ost_write',
                      'ost_get_info', 'ost_connect', 'ost_punch', 'ost_statfs', 'ost_sync', 'ost_quotactl',
                      'ldlm_cancel', 'obd_ping']
        second_list = ['pending_read_pages', 'read_RPCs_in_flight', 'avg_waittime', 'inflight', 'unregistering',
                       'timeouts', 'req_waittime', 'req_active', 'mds_getattr', 'mds_getattr_lock', 'mds_close',
                       'mds_readpage', 'mds_connect', 'mds_get_root', 'mds_statfs', 'mds_sync', 'mds_quotactl',
                       'mds_getxattr', 'mds_hsm_state_set', 'ldlm_cancel', 'obd_ping', 'seq_query', 'fld_query',
                       'close', 'create', 'enqueue', 'getattr', 'intent_lock', 'link', 'rename', 'setattr', 'fsync',
                       'read_page', 'unlink', 'setxattr', 'getxattr', 'intent_getattr_async', 'revalidate_lock']

        id_ = len(list_)
        previous_key = ""
        while True:
            if previous_key:
                list_[id_] = previous_key
            if row[id_] in first_list:
                previous_key = row[id_]
            elif not previous_key:
                break
            else:
                previous_key = ""
            id_ += 1
        for i in ["pending_read_pages", "read_RPCs_in_flight", "avg_waittime_md1", "inflight_md1", "unregistering_md1",
                  "timeouts_md1"]:
            list_[id_] = i
            id_ += 1
        previous_key = ""
        while True:

            if previous_key:
                list_[id_] = previous_key + "_md1"
            if row[id_] in second_list:
                previous_key = row[id_]
            elif not previous_key:
                break
            else:
                previous_key = ""
            id_ += 1
        list_[id_] = "label_value"
        id_ += 1
        list_[id_] = "date_time"
        return list_

    def combine_logs(self, mainDict, headers):
        max_index_lst = [3, 6, 7, 8]
        total_sum_index = [2, 4, 5, 6, 11]
        main_lst = {}
        # print(mainDict)
        for key in mainDict:
            lst = []
            for i in range(len(mainDict[key][0]) - 1):
                to_append = 0
                if i not in max_index_lst:
                    total = 0
                    count = 0
                    for j in range(len(mainDict[key])):
                        total += mainDict[key][j][i]
                        count += 1

                    average_val = float(total / count)
                    if i in total_sum_index:
                        to_append = total
                    else:
                        to_append = average_val
                else:
                    max_val = -10000
                    for j in range(len(mainDict[key])):
                        if float(mainDict[key][j][i]) > max_val:
                            max_val = mainDict[key][j][i]
                    to_append = max_val

                id_ = self.attr_to_id[headers[i]]
                type_ = self.datatypes[id_]
                lst.append(self.get_data_type(to_append, type_))
            lst.append(int(mainDict[key][0][-1]))
            key_ = int(mainDict[key][0][-1])
            if key_ not in main_lst:
                main_lst[key_] = []
            main_lst[key_].append(lst)
        return main_lst

    def is_number(self, string_):
        try:
            complex(string_)  # for int, long, float and complex
        except ValueError:
            return False
        return True

    def read_data_from_folder_file(self, folder_list):
        total_columns = 0
        exclude_list = [21, 22, 23, 24, 25, 26, 27, 36, 37, 40, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 56, 57, 59, 63,
                        64, 65, 66, 67, 68, 69, 70]

        def not_in_exclude_list(val, exclude_list):
            return val not in exclude_list

        cols = []
        cols_headers = []
        cols_index = []
        cols_list = {}
        mainDict = {}
        if len(folder_list) > 0:
            for filename in folder_list:
                if "csv" in filename:
                    df = pd.read_csv(filename, header=None)
                    row = list(df.iloc[1, :])
                    cols_list = self.get_info_list(row)
                    for i in exclude_list:
                        cols_list.pop(i)
                    cols_list.pop(sorted(list(cols_list.keys()))[-1])

                    cols_index = sorted([x for x in cols_list if not_in_exclude_list(x, exclude_list) is True])
                    cols_headers = [cols_list[i] for i in cols_index]
                break
        for filename in folder_list:
            if "csv" in filename:
                with open(filename, 'rb') as in_file:
                    for line in in_file:
                        line = str(line).lstrip('b\'')
                        parts = str(line).split(",")
                        date = parts[-1].strip("'")
                        key = date[:-2]

                        parts_without_date = parts[:-1]
                        lst = []
                        count = 0
                        for i in range(len(parts_without_date)):
                            if i in cols_index:
                                part = parts_without_date[i]
                                if self.is_number(part):
                                    id_ = self.attr_to_id[cols_list[i]]
                                    type_ = self.datatypes[id_]
                                    tmp_val = self.get_data_type(part, type_)

                                    lst.append(tmp_val)
                        if not total_columns:
                            total_columns = len(lst)
                        if len(lst) == total_columns:
                            mainDict.setdefault(key, []).append(lst)
        return mainDict, cols_headers

    def add_all_dataset_files(self, folder):
        files = os.listdir(folder)
        if self.file_system == "normal":
            for filename in files:
                if "dataset" in filename and "csv" in filename:
                    print("[+] Starting for %s" % (filename))
                    self.write_to_proto(folder + "/" + filename)
        elif self.file_system == "lustre":
            folder_list = glob.glob(folder + "*")
            mainDict, headers = self.read_data_from_folder_file(folder_list)
            main_list = self.combine_logs(mainDict, headers)
            self.aws_write(main_list, headers)
        else:
            for filename in files:
                if "csv" in filename and "aws" in filename:
                    self.write_to_proto(folder + "/" + filename)

    def check_serialize_file(self, serialize_file):
        full_path = self.binary_dir + "/" + self.environment + "/" + serialize_file
        bottleneck_logs = bottleneck_pb2.BottleneckFiles()
        if os.path.isfile(full_path):
            try:
                f = open(full_path, "rb")
                bottleneck_logs.ParseFromString(f.read())
                f.close()
            except IOError:
                print(full_path + ": Could not open file.  Creating a new one.")
        return bottleneck_logs


folder_dir = "./csv_logs/DTNS"
serialize_file = folder_dir.split("/")[-2]
csv_to_python = CSV_to_Proto(folder_dir, serialize_file)
csv_to_python.add_all_dataset_files(csv_to_python.folder_name)
csv_to_python.write_to_binary(csv_to_python.serialize_file)
