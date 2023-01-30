from collections import Counter

from pandas import DataFrame

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
        self.dataframe_dir = "./dataframe_logs"
        Path(self.dataframe_dir).mkdir(parents=True, exist_ok=True)
        self.network_type = {"DTNS": 0, "AWS": 1, "CC": 2, "AWS_FXS": 3, "CLOUDLAB": 4}
        self.anomaly_side = {"SENDER": 0, "RECEIVER": 1, "NOSIDE": 3}
        self.environment = "CLOUDLAB" if self.folder_name.split("/")[2].upper() not in self.network_type else \
            self.folder_name.split("/")[2]
        # self.file_system = "normal" if "FXS" not in self.environment else "lustre"
        self.file_system = "lustre"
        # self.bottleneck_logs = self.check_serialize_file(self.serialize_file)
        self.log_list = []
        self.metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate', 4: 'avg_retransmission_timeout_value',
                                   5: 'byte_ack', 6: 'seg_out', 7: 'retrans', 8: 'mss_value', 9: 'ssthresh_value',
                                   10: 'segs_in', 11: 'avg_send_value', 12: 'unacked_value', 13: 'rcv_space',
                                   14: 'send_buffer_value', 15: 'avg_dsack_dups_value', 16: 'avg_reord_seen',

                                   17: 'rchar', 18: 'wchar', 19: 'syscr', 20: 'syscw', 21: 'read_bytes_io',
                                   22: 'write_bytes_io', 23: 'cancelled_write_bytes', 24: 'pid', 25: 'ppid', 26: 'pgrp',
                                   27: 'session', 28: 'tty_nr', 29: 'tpgid', 30: 'flags', 31: 'minflt', 32: 'cminflt',
                                   33: 'majflt', 34: 'cmajflt', 35: 'utime', 36: 'stime', 37: 'cutime', 38: 'cstime',
                                   39: 'priority', 40: 'nice', 41: 'num_threads', 42: 'itrealvalue', 43: 'starttime',
                                   44: 'vsize', 45: 'rss', 46: 'rsslim', 47: 'startcode', 48: 'endcode',
                                   49: 'startstack', 50: 'kstkesp', 51: 'kstkeip', 52: 'signal', 53: 'blocked',
                                   54: 'sigignore', 55: 'sigcatch', 56: 'wchan', 57: 'nswap', 58: 'cnswap',
                                   59: 'exit_signal', 60: 'processor', 61: 'rt_priority', 62: 'policy',
                                   63: 'delayacct_blkio_ticks', 64: 'guest_time', 65: 'cguest_time', 66: 'start_data',
                                   67: 'end_data', 68: 'start_brk', 69: 'arg_start', 70: 'arg_end', 71: 'env_start',
                                   72: 'env_end', 73: 'exit_code', 74: 'cpu_usage_percentage', 75: 'mem_usage_percentage',

                                   76: 'tcp_rcv_buffer_min', 77: 'tcp_rcv_buffer_default', 78: 'tcp_rcv_buffer_max',
                                   79: 'tcp_snd_buffer_min', 80: 'tcp_snd_buffer_default', 81: 'tcp_snd_buffer_max',

                                   82: 'req_waittime', 83: 'req_active', 84: 'read_bytes', 85: 'write_bytes',
                                   86: 'ost_setattr', 87: 'ost_read', 88: 'ost_write', 89: 'ost_get_info',
                                   90: 'ost_connect', 91: 'ost_punch', 92: 'ost_statfs', 93: 'ost_sync',
                                   94: 'ost_quotactl', 95: 'ldlm_cancel', 96: 'obd_ping', 97: 'pending_read_pages',
                                   98: 'read_RPCs_in_flight',

                                   99: 'avg_waittime_md', 100: 'inflight_md', 101: 'unregistering_md',
                                   102: 'timeouts_md', 103: 'req_waittime_md', 104: 'req_active_md',
                                   105: 'mds_getattr_md', 106: 'mds_getattr_lock_md', 107: 'mds_close_md',
                                   108: 'mds_readpage_md', 109: 'mds_connect_md', 110: 'mds_get_root_md',
                                   111: 'mds_statfs_md', 112: 'mds_sync_md', 113: 'mds_quotactl_md',
                                   114: 'mds_getxattr_md', 115: 'mds_hsm_state_set_md', 116: 'ldlm_cancel_md',
                                   117: 'obd_ping_md', 118: 'seq_query_md', 119: 'fld_query_md', 120: 'close_md',
                                   121: 'create_md', 122: 'enqueue_md', 123: 'getattr_md', 124: 'intent_lock_md',
                                   125: 'link_md', 126: 'rename_md', 127: 'setattr_md', 128: 'fsync_md',
                                   129: 'read_page_md', 130: 'unlink_md', 131: 'setxattr_md', 132: 'getxattr_md',
                                   133: 'intent_getattr_async_md', 134: 'revalidate_lock_md',

                                   135: 'system_cpu_percent', 136: 'system_memory_percent',

                                   137: 'nic_send_bytes', 138:'nic_receive_bytes',

                                   139: 'remote_ost_read_bytes', 140: 'remote_ost_write_bytes',

                                   141: 'dtn_lustre_read_bytes', 142:'dtn_lustre_write_bytes',
                                   }
        self.log_id_to_attr = {1: 'time_stamp', 2: 'sender_metrics', 3: 'receiver_metrics',
                               4: 'through_put', 5: 'label_value'}

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
        self.log_data_types = {1: 'float', 4: 'float', 5: 'int'}
        # self.mdt_stat_datatypes = {1: 'int', 2: 'int', 3: 'int', 4: 'int', 5: 'int', 6: 'int', 7: 'int',
        #                            8: 'int', 9: 'int', 10: 'int', 11: 'int', 12: 'int', 13: 'int', 14: 'int', 15: 'int',
        #                            16: 'int', 17: 'int', 18: 'int', 19: 'int', 20: 'int', 21: 'int', 22: 'int',
        #                            23: 'int', 24: 'int', 25: 'int', 26: 'int', 27: 'int', 28: 'int', 29: 'int',
        #                            30: 'int', 31: 'int', 32: 'int', 33: 'int', 34: 'int', 35: 'int', 36: 'int'}
        # # TODO complete this file type
        # self.filetype = {0: {}, 1: {'read_threads': 1}}
        # self.protobuff_files = {}
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
            # self.keys = list(range(1, 16))
            self.keys = list(range(1, 143))
            # self.keys = list(range(1, 15)) + list(range(30, 110)) + list(range(112, 148)) + [148, 149, 150, 151, 152, 153, 154]

    def read_csv(self, filename):
        data = []
        # if self.file_system == "lustre":
        #     get_new_row = self.get_new_row_lustre
        # else:
        #     get_new_row = self.get_new_row_normal
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            count = 0
            for row in csv_reader:
                # data.append(get_new_row(row))
                data.append(row)
        return data

    # def get_data_type(self, val, type_):
    #     if type_ == "string":
    #         return float(self.get_mbps(val))
    #     elif type_ == "float":
    #         return float(val)
    #     elif type_ == "intonly":
    #         tmp_value = str(val).split(".")[0]
    #         return int(tmp_value)
    #     elif type_ == "dict":
    #         pass
    #     else:
    #         return int(float(val))
    #
    # def get_mbps(self, thpt):
    #     if self.is_number(thpt):
    #         return thpt
    #     thpts = thpt.split("Gb")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) * 1024
    #     thpts = thpt.split("Mb")
    #     if len(thpts) == 2:
    #         return float(thpts[0])
    #     thpts = thpt.split("Kb")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) / 1024.
    #     thpts = thpt.split("b")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) / (1024. * 1024.)
    #     thpts = thpt.split("MB")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) * 8
    #     thpts = thpt.split("KB")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) * 8 / 1024.
    #     thpts = thpt.split("B")
    #     if len(thpts) == 2:
    #         return float(thpts[0]) * 8 / 1024. * 1024.
    #     try:
    #         return float(thpt)
    #     except:
    #         return 0.0

    def get_file_id(self, filename):
        number_compile = re.compile('\d+')
        return int(number_compile.findall(filename.split("/")[-1])[0])

    def write_to_dataframe(self, filename):
        log_list_temp = []
        logs = self.read_csv(filename)
        length_log = 0 if len(logs) == 0 else len(logs[0])
        for log in logs:
            new_log = {}
            # new_log = bottleneck_pb2.BottleneckLog()
            # new_sender_metrics = bottleneck_pb2.BottleneckMetrics()
            # new_receiver_metrics = bottleneck_pb2.BottleneckMetrics()
            if self.file_system == "normal":
                print("IMPLEMENT THIS")
                # # log[0]
                # new_log.__setattr__(self.log_id_to_attr[1], log[0])
                # # sender_logs = log[1:99]
                # total_keys_number = len(self.keys)
                # for i in range(total_keys_number):
                #     new_log.sender_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1])
                # # receiver_logs = log[99:-1]
                # for i in range(total_keys_number):
                #     new_log.receiver_metrics.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i + 1 + total_keys_number])
                # new_log.__setattr__(self.log_id_to_attr[4], log[-1])
                # # for i in range(len(self.keys)):
                # #     new_log.__setattr__(self.metrics_id_to_attr[self.keys[i]], log[i])
            else:
                #log[0] timestamp
                new_log[self.log_id_to_attr[1]] = log[0]
                # sender_logs = log[1:139]
                total_keys_number = len(self.keys)
                for i in range(total_keys_number):
                    tmp_key = "sender_{}".format(self.metrics_id_to_attr[self.keys[i]])
                    new_log[tmp_key] = log[i + 1]
                # receiver_logs = log[139:277]
                for i in range(total_keys_number):
                    tmp_key = "receiver_{}".format(self.metrics_id_to_attr[self.keys[i]])
                    new_log[tmp_key] = log[i + 1 + total_keys_number]

                # through_put log [278]
                new_log[self.log_id_to_attr[4]] = log[-2]

                # label value log [279]
                new_log[self.log_id_to_attr[5]] = log[-1]

                # new_log.__setattr__("label_value", log[-1])
            log_list_temp.append(new_log)
        print("[+] The number of the rows is %d" % len(log_list_temp))
        self.log_list += log_list_temp

    def create_dataframe(self, serialize_file):
        try:
            file_path = "{}/{}/{}.csv".format(self.dataframe_dir, self.environment, serialize_file)
            Path(self.dataframe_dir + "/" + self.environment).mkdir(parents=True, exist_ok=True)
            dataframe = pd.DataFrame(self.log_list)
            print(len(dict(Counter(dataframe[dataframe.columns[len(dataframe.columns) - 1]]))),"labels")

            dataframe.to_csv(file_path, index=False)
            # f = open(file_path, "wb")
            # f.write(self.bottleneck_logs.SerializeToString())
            # f.close()
            print("dataframe with path: " + file_path + " is created.")
        except IOError:
            print("[+] Error while creating binary file.")

    def is_number(self, string_):
        try:
            complex(string_)  # for int, long, float and complex
        except ValueError:
            return False
        return True

    def add_all_dataset_files(self, folder):
        files = os.listdir(folder)
        if self.file_system == "lustre":
            for filename in files:
                if "dataset" in filename and "csv" in filename:
                    print("[+] Starting for %s" % (filename))
                    self.write_to_dataframe(folder + "/" + filename)
        else:
            for filename in files:
                if "csv" in filename and "aws" in filename:
                    self.write_to_dataframe(folder + "/" + filename)


# folder_dir = "./csv_logs/V3/wisconsine-220g1-ssd/"
# folder_dir = "./csv_logs/V3/wisconsine-220g1-HDD/"

# folder_dir = "./csv_logs/V3/wisconsin-220g2-ssd/"
# folder_dir = "./csv_logs/V3/wisconsine-220g2-hdd/"
# folder_dir = "./csv_logs/V3/utah-652525g-ssd/"
# folder_dir = "./csv_logs/V3/utah-6525-25-ssd-delayed-30ms/"
# folder_dir = "./csv_logs/V3/wisconsine-220g2-hdd-ssd/"
# folder_dir = "./csv_logs/V3/wisconsin-220g2-ssd-delayed-10ms/"
# folder_dir = "./csv_logs/V3/utah-6525-25-ssd-delayed-10ms/"
folder_dir = "./csv_logs/V3/wisconsin-220g2-hdd-delayed-10ms/"
# folder_dir = "./csv_logs/V3/wisconsin-220g2-ssd-simultanious-v2/"

if not folder_dir.endswith('/'):
    src_path = folder_dir + "/"
# serialize_file = "emulab_d460_10Gbps_hdd_unmerged_all_cols_V2"
# serialize_file = "utah_c6525-25g_25Gbps_ssd_unmerged_all_cols_V2"
# serialize_file = "wisconsin_c220g1-10Gbps_ssd_unmerged_all_cols_V2"
# serialize_file = "utah_c6525-25g_1Gbps_ssd_unmerged_all_cols_V2"
# serialize_file = "wisconsin_c220g1-10Gbps_hdd_ssd_unmerged_all_cols_V2"
# serialize_file = "wisconsin_c220g1-10Gbps_hdd_ssd_unmerged_all_cols_V2"


# serialize_file = "utah-6525-25g-25Gbps_ssd_unmerged_all_cols_V3"
# serialize_file = "wisconsin-220g2-10Gbps_ssd_unmerged_all_cols_V3"
# serialize_file = "wisconsine-220g2-10Gbps_hdd_unmerged_all_cols_V3"
# serialize_file = "utah-6525-25-ssd-delayed-30ms_unmerged_all_cols_V3"
# serialize_file = "wisconsine-220g2-hdd-ssd_unmerged_all_cols_V3"
# serialize_file = "wisconsin-220g2-ssd-delayed-10ms_unmerged_all_cols_V3"
# serialize_file = "utah-6525-25-ssd-delayed-10ms_unmerged_all_cols_V3"
serialize_file = "wisconsin-220g2-hdd-delayed-10ms_unmerged_all_cols_V3"
# serialize_file = "wisconsin-220g2-ssd-simultanious-v2_unmerged_all_cols_V3"

csv_to_python = CSV_to_Proto(folder_dir, serialize_file)
csv_to_python.add_all_dataset_files(csv_to_python.folder_name)
csv_to_python.create_dataframe(csv_to_python.serialize_file)
