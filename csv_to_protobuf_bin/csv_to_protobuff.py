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
        self.anomaly_side = {"SENDER": 0, "RECEIVER": 1, "NOSIDE": 3}
        self.environment = "UNDEFINED" if self.folder_name.split("/")[2].upper() not in self.network_type else \
            self.folder_name.split("/")[2]
        self.file_system = "normal" if "FXS" not in self.environment else "lustre"
        self.bottleneck_logs = self.check_serialize_file(self.serialize_file)
        self.metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate', 4: 'avg_retransmission_timeout_value',
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

                                   110: 'pending_read_pages', 111: 'read_RPCs_in_flight', 112: 'avg_waittime_md',
                                   113: 'inflight_md', 114: 'unregistering_md', 115: 'timeouts_md', 116: 'req_waittime_md',
                                   117: 'req_active_md', 118: 'mds_getattr_md', 119: 'mds_getattr_lock_md',
                                   120: 'mds_close_md', 121: 'mds_readpage_md', 122: 'mds_connect_md',
                                   123: 'mds_get_root_md', 124: 'mds_statfs_md', 125: 'mds_sync_md', 126: 'mds_quotactl_md',
                                   127: 'mds_getxattr_md', 128: 'mds_hsm_state_set_md', 129: 'ldlm_cancel_md',
                                   130: 'obd_ping_md', 131: 'seq_query_md', 132: 'fld_query_md', 133: 'close_md',
                                   134: 'create_md', 135: 'enqueue_md', 136: 'getattr_md', 137: 'intent_lock_md',
                                   138: 'link_md', 139: 'rename_md', 140: 'setattr_md', 141: 'fsync_md',
                                   142: 'read_page_md', 143: 'unlink_md', 144: 'setxattr_md', 145: 'getxattr_md',
                                   146: 'intent_getattr_async_md', 147: 'revalidate_lock_md',
                                   148: 'avg_dsack_dups_value', 149: 'avg_reord_seen',
                                   150: 'system_cpu_percent', 151: 'system_memory_percent',
                                   152: 'remote_ost_read_bytes', 153: 'remote_ost_write_bytes'}
        self.log_id_to_attr = {1: 'time_stamp', 2: 'sender_metrics',
                               3: 'receiver_metrics', 4: 'label_value'}
        # self.mdt_stat_id_to_attr = {1: 'avg_waittime', 2: 'inflight', 3: 'unregistering', 4: 'timeouts',
        #                            5: 'req_waittime', 6: 'req_active', 7: 'mds_getattr', 8: 'mds_getattr_lock',
        #                            9: 'mds_close', 10: 'mds_readpage', 11: 'mds_connect', 12: 'mds_get_root',
        #                            13: 'mds_statfs', 14: 'mds_sync', 15: 'mds_quotactl', 16: 'mds_getxattr',
        #                            17: 'mds_hsm_state_set', 18: 'ldlm_cancel', 19: 'obd_ping', 20: 'seq_query',
        #                            21: 'fld_query', 22: 'close', 23: 'create', 24: 'enqueue',
        #                            25: 'getattr', 26: 'intent_lock', 27: 'link', 28: 'rename',
        #                            29: 'setattr', 30: 'fsync', 31: 'read_page', 32: 'unlink',
        #                            33: 'setxattr', 34: 'getxattr', 35: 'intent_getattr_async', 36: 'revalidate_lock'}

        self.metrics_attr_to_id = {}
        for i in self.metrics_id_to_attr:
            self.metrics_attr_to_id[self.metrics_id_to_attr[i]] = i
        self.logs_attr_to_id = {}
        for i in self.log_id_to_attr:
            self.logs_attr_to_id[self.log_id_to_attr[i]] = i
            # self.mdt_stat_attr_to_id = {}
        # for i in self.mdt_stat_id_to_attr:
        #     self.mdt_stat_attr_to_id[self.mdt_stat_id_to_attr[i]] = i
        self.metrics_datatypes = {1: 'float', 2: 'string', 3: 'float', 4: 'float', 5: 'float', 6: 'float', 7: 'float',
                                  8: 'float', 9: 'float', 10: 'float', 11: 'string', 12: 'float', 13: 'float', 14: 'float',
                                  15: 'float', 16: 'float', 17: 'float', 18: 'float', 19: 'float', 20: 'float', 21: 'float',
                                  22: 'float', 23: 'float', 24: 'float', 25: 'float', 26: 'float', 27: 'float', 28: 'float',
                                  29: 'float', 30: 'int', 31: 'int', 32: 'int', 33: 'int', 34: 'int', 35: 'int', 36: 'int',
                                  37: 'int', 38: 'int', 39: 'int', 40: 'int', 41: 'int', 42: 'int', 43: 'int', 44: 'int',
                                  45: 'int', 46: 'int', 47: 'int', 48: 'int', 49: 'int', 50: 'int', 51: 'int', 52: 'int',
                                  53: 'int', 54: 'int', 55: 'int', 56: 'int', 57: 'int', 58: 'int',
                                  59: 'intonly', 60: 'intonly', 61: 'intonly', 62: 'intonly', 63: 'int', 64: 'int', 65: 'int',
                                  66: 'int', 67: 'int', 68: 'int', 69: 'float', 70: 'int', 71: 'int', 72: 'int', 73: 'int',
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
                                  148: 'float', 149: 'float', 150: 'float', 151: 'float',
                                  152: 'int', 153: 'int'}
        self.log_data_types = {1: 'float', 4: 'int'}
        # self.mdt_stat_datatypes = {1: 'int', 2: 'int', 3: 'int', 4: 'int', 5: 'int', 6: 'int', 7: 'int',
        #                            8: 'int', 9: 'int', 10: 'int', 11: 'int', 12: 'int', 13: 'int', 14: 'int', 15: 'int',
        #                            16: 'int', 17: 'int', 18: 'int', 19: 'int', 20: 'int', 21: 'int', 22: 'int',
        #                            23: 'int', 24: 'int', 25: 'int', 26: 'int', 27: 'int', 28: 'int', 29: 'int',
        #                            30: 'int', 31: 'int', 32: 'int', 33: 'int', 34: 'int', 35: 'int', 36: 'int'}
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
                         32: {'write_threads': 128}, 33: {'cpu_stress': 10}, 34: {'io_stress': 10},
                         35: {'mem_stress': 0.98}, 36: {'link_loss': 0.5}, 37: {'link_loss': 0.1},
                         38: {'link_loss': 0.05}, 39: {'link_loss': 1},
                         40: {'link_delay': 0.1, "link_delay_distribution": 0},
                         41: {'link_delay': 0.1, "link_delay_distribution": 0},
                         42: {'link_delay': 0.1, "link_delay_distribution": 0},
                         43: {'link_delay': 0.1, "link_delay_distribution": 0},
                         44: {'link_duplicate': 10}, 45: {'link_duplicate': 15},
                         46: {'link_duplicate': 20}, 47: {'link_duplicate': 25},
                         48: {'link_corrupt': 0.5}, 49: {'link_corrupt': 0.1},
                         50: {'link_corrupt': 0.05}, 51: {'link_corrupt': 1},
                         52: {'link_delay': 1.0, 'link_reorder': 10}, 53: {'link_delay': 1.0, 'link_reorder': 15},
                         54: {'link_delay': 1.0, 'link_reorder': 20}, 55: {'link_delay': 1.0, 'link_reorder': 25},
                         56: {'cpu_stress': 30}, 57: {'cpu_stress': 70}, 58: {'cpu_stress': 100},
                         59: {'max_buffer_size_ratio': 0.5}, 60: {'max_buffer_size_ratio': 0.25},
                         61: {'max_buffer_size_ratio': 0.125},
                         62: {'read_threads': 2}, 63: {'read_threads': 4}, 64: {'read_threads': 8},
                         65: {'read_threads': 16},
                         66: {'write_threads': 4}, 67: {'write_threads': 8}, 68: {'write_threads': 16},
                         69: {'write_threads': 32}, 70: {'write_threads': 48}, 71: {'write_threads': 64},
                         72: {'write_threads': 96}, 73: {'write_threads': 128},
                         74: {'write_threads': 4}, 75: {'write_threads': 8}, 76: {'write_threads': 16},
                         77: {'write_threads': 24}, 78: {'write_threads': 32}, 79: {'write_threads': 64},
                         80: {'write_threads': 96}, 81: {'write_threads': 128},
                         82: {'cpu_stress': 10}, 83: {'cpu_stress': 30}, 84: {'cpu_stress': 70},
                         85: {'cpu_stress': 100},
                         86: {'io_stress': 10},
                         87: {'mem_stress': 0.98},
                         88: {'max_buffer_size_ratio': 0.5}, 89: {'max_buffer_size_ratio': 0.25},
                         90: {'max_buffer_size_ratio': 0.125}}
        self.protobuff_files = {}
        if self.file_system == "normal":
            self.keys = list(range(1, 95)) + [148, 149, 150, 151]
        else:
            # 14 metrics for ss command 1-14
            # 65 metrics for process info, tcp buffer values 30-94
            # 15 metrics for osc-ost stat 95-109
            # 15 metrics for osc-ost stat 110-111
            # 36 metrics for mdc-mdt stats 112-147
            # 4 metrics for more network and system cpu and memory status 148-153
            # 1 metric label value
            self.keys = list(range(1, 15)) + list(range(30, 148)) + [148, 149, 150, 151, 152, 153]
            # self.keys = list(range(1, 15)) + list(range(30, 110)) + list(range(112, 148)) + [148, 149, 150, 151, 152, 153, 154]

    # TODO must be changes according to the size of self.keys
    def get_new_row_normal(self, row):
        new_row = []
        # row[0]
        type_ = self.log_data_types[1]
        new_row.append(self.get_data_type(row[0], type_))
        # row[1:99]
        total_keys_number = len(self.keys)
        for i in range(total_keys_number):
            type_ = self.metrics_datatypes[self.keys[i]]
            new_row.append(self.get_data_type(row[i+1], type_))
        # row[99:-1]
        for i in range(total_keys_number):
            type_ = self.metrics_datatypes[self.keys[i]]
            new_row.append(self.get_data_type(row[i+1+total_keys_number], type_))
        # row[-1]
        type_ = self.log_data_types[4]
        new_row.append(self.get_data_type(row[-1], type_))

        # for i in range(len(row)):
        #     type_ = self.metrics_datatypes[self.keys[i]]
        #     new_row.append(self.get_data_type(row[i], type_))
        return new_row

    def get_new_row_lustre(self, row):
        new_row = []
        # row[0]
        type_ = self.log_data_types[1]
        new_row.append(self.get_data_type(row[0], type_))
        # row[1:139]
        total_keys_number = len(self.keys)
        for i in range(total_keys_number):
            type_ = self.metrics_datatypes[self.keys[i]]
            new_row.append(self.get_data_type(row[i+1], type_))

        # row[139:-1]
        for i in range(total_keys_number):
            type_ = self.metrics_datatypes[self.keys[i]]
            new_row.append(self.get_data_type(row[i+1+total_keys_number], type_))
        # row[-1]
        type_ = self.log_data_types[4]
        new_row.append(self.get_data_type(row[-1], type_))
        # for i in range(101):
        #     type_ = self.datatypes[self.keys[i]]
        #     new_row.append(self.get_data_type(row[i], type_))
        # total_mdt_numbers = new_row[100]
        # # add mdt stat maps to list of metrics
        # mdt_stats_dict = {}
        # for i in range(total_mdt_numbers):
        #     new_mdt_stat_start_index = 101 + i * 37
        #     new_mdt_stat_list = []
        #     for j in self.mdt_stat_id_to_attr.keys():
        #         type_ = self.mdt_stat_datatypes[j]
        #         new_mdt_stat_list.append(self.get_data_type(row[new_mdt_stat_start_index + j], type_))
        #     mdt_stats_dict[row[new_mdt_stat_start_index]] = new_mdt_stat_list
        # new_row.append(mdt_stats_dict)
        # # add label value
        # type_ = self.datatypes[self.keys[-1]]
        # new_row.append(self.get_data_type(row[-1], type_))

        return new_row

    def read_csv(self, filename):
        data = []
        if self.file_system == "lustre":
            get_new_row = self.get_new_row_lustre
        else:
            get_new_row = self.get_new_row_normal
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count = 0
            for row in csv_reader:
                # skip first row
                # if count == 0:
                #     count += 1
                #     continue
                new_row = []
                # for i in range(len(row)):
                #     type_ = self.datatypes[self.keys[i]]
                #     new_row.append(self.get_data_type(row[i], type_))
                data.append(get_new_row(row))
        return data

    def get_data_type(self, val, type_):
        if type_ == "string":
            return float(self.get_mbps(val))
        elif type_ == "float":
            return float(val)
        elif type_ == "intonly":
            tmp_value = str(val).split(".")[0]
            return int(tmp_value)
        elif type_ == "dict":
            pass
        else:
            return int(float(val))

    def get_mbps(self, thpt):
        if self.is_number(thpt):
            return thpt
        thpts = thpt.split("Gb")
        if len(thpts) == 2:
            return float(thpts[0]) * 1024
        thpts = thpt.split("Mb")
        if len(thpts) == 2:
            return float(thpts[0])
        thpts = thpt.split("Kb")
        if len(thpts) == 2:
            return float(thpts[0]) / 1024.
        thpts = thpt.split("b")
        if len(thpts) == 2:
            return float(thpts[0]) / (1024. * 1024.)
        thpts = thpt.split("MB")
        if len(thpts) == 2:
            return float(thpts[0]) * 8
        thpts = thpt.split("KB")
        if len(thpts) == 2:
            return float(thpts[0]) * 8 / 1024.
        thpts = thpt.split("B")
        if len(thpts) == 2:
            return float(thpts[0]) * 8 / 1024. * 1024.
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
        # if self.file_system == "normal":
        id_ = self.get_file_id(filename)
        if id_ not in self.protobuff_files:
            self.protobuff_files[id_] = bottleneck_pb2.BottleneckFile()
        this_file_logs = self.protobuff_files[id_]
        attrs = self.filetype[id_]
        for i in attrs:
            this_file_logs.__setattr__(i, attrs[i])
        this_file_logs.__setattr__("network_type", self.network_type[self.environment.upper()])
        this_file_logs.__setattr__("created_time_utc", os.path.getctime(filename))
        if 0 < id_ < 66:
            this_file_logs.__setattr__("anomaly_side", self.anomaly_side["SENDER"])
        elif id_ >= 66:
            this_file_logs.__setattr__("anomaly_side", self.anomaly_side["RECEIVER"])
        else:
            this_file_logs.__setattr__("anomaly_side", self.anomaly_side["NOSIDE"])
        length_log = 0 if len(logs) == 0 else len(logs[0])
        for log in logs:
            new_log = bottleneck_pb2.BottleneckLog()
            new_sender_metrics = bottleneck_pb2.BottleneckMetrics()
            new_receiver_metrics = bottleneck_pb2.BottleneckMetrics()
            if self.file_system == "normal":
                # log[0]
                new_log.__setattr__(self.log_id_to_attr[1], log[0])
                # sender_logs = log[1:99]
                total_keys_number = len(self.keys)
                for i in range(total_keys_number):
                    new_log.sender_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1])
                # receiver_logs = log[99:-1]
                for i in range(total_keys_number):
                    new_log.receiver_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1 + total_keys_number])
                new_log.__setattr__(self.log_id_to_attr[4], log[-1])
                # for i in range(len(self.keys)):
                #     new_log.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i])
            else:
                #log[0]
                new_log.__setattr__(self.log_id_to_attr[1], log[0])
                # sender_logs = log[1:139]
                total_keys_number = len(self.keys)
                for i in range(total_keys_number):
                    new_log.sender_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1])
                # receiver_logs = log[139:-1]
                # new_log.__setattr__(self.log_id_to_attr[2], new_sender_metrics)
                for i in range(total_keys_number):
                    new_log.receiver_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1 + total_keys_number])
                # new_log.__setattr__(self.log_id_to_attr[3], new_receiver_metrics)
                new_log.__setattr__(self.log_id_to_attr[4], log[-1])
                #print(new_log)
                # for i in range(101):
                #     new_log.__setattr__(self.id_to_attr[self.keys[i]], log[i])
                # for mdt_name in log[101].keys():
                #     value_list = log[101].get(mdt_name) or []
                #     for i, value in enumerate(value_list):
                #         new_log.mdt_stats_map[mdt_name].__setattr__(self.mdt_stat_id_to_attr[i + 1], value)

                # new_log.__setattr__("label_value", log[-1])
            this_file_logs.rows.append(new_log)
        print("[+] The number of the rows is %d" % len(this_file_logs.rows))
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
        for i in ["pending_read_pages", "read_RPCs_in_flight", "avg_waittime_md", "inflight_md", "unregistering_md",
                  "timeouts_md"]:
            list_[id_] = i
            id_ += 1
        previous_key = ""
        while True:

            if previous_key:
                list_[id_] = previous_key + "_md"
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

                id_ = self.metrics_attr_to_id[headers[i]]
                type_ = self.metrics_datatypes[id_]
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
                                    id_ = self.metrics_attr_to_id[cols_list[i]]
                                    type_ = self.metrics_datatypes[id_]
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
            for filename in files:
                if "dataset" in filename and "csv" in filename:
                    print("[+] Starting for %s" % (filename))
                    self.write_to_proto(folder + "/" + filename)
            # folder_list = glob.glob(folder + "*")
            # mainDict, headers = self.read_data_from_folder_file(folder_list)
            # main_list = self.combine_logs(mainDict, headers)
            # self.aws_write(main_list, headers)
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


folder_dir = "./csv_logs/DTNS/series14/"
if not folder_dir.endswith('/'):
    src_path = folder_dir + "/"
serialize_file = folder_dir.split("/")[-2]
csv_to_python = CSV_to_Proto(folder_dir, serialize_file)
csv_to_python.add_all_dataset_files(csv_to_python.folder_name)
csv_to_python.write_to_binary(csv_to_python.serialize_file)
