import csv


class DataConverter:
    def __init__(self, file_system="normal", prefix=""):
        self.prefix = prefix
        self.file_system = file_system
        self.log_data_types = {1: 'float', 4: 'int'}
        self.metrics_datatypes = {1: 'float', 2: 'string', 3: 'float', 4: 'float', 5: 'float', 6: 'float', 7: 'float',
                                  8: 'float', 9: 'float', 10: 'float', 11: 'string', 12: 'float', 13: 'float',
                                  14: 'float',
                                  15: 'float', 16: 'float', 17: 'float', 18: 'float', 19: 'float', 20: 'float',
                                  21: 'float',
                                  22: 'float', 23: 'float', 24: 'float', 25: 'float', 26: 'float', 27: 'float',
                                  28: 'float',
                                  29: 'float', 30: 'int', 31: 'int', 32: 'int', 33: 'int', 34: 'int', 35: 'int',
                                  36: 'int',
                                  37: 'int', 38: 'int', 39: 'int', 40: 'int', 41: 'int', 42: 'int', 43: 'int',
                                  44: 'int',
                                  45: 'int', 46: 'int', 47: 'int', 48: 'int', 49: 'int', 50: 'int', 51: 'int',
                                  52: 'int',
                                  53: 'int', 54: 'int', 55: 'int', 56: 'int', 57: 'int', 58: 'int',
                                  59: 'intonly', 60: 'intonly', 61: 'intonly', 62: 'intonly', 63: 'int', 64: 'int',
                                  65: 'int',
                                  66: 'int', 67: 'int', 68: 'int', 69: 'float', 70: 'int', 71: 'int', 72: 'int',
                                  73: 'int',
                                  74: 'int', 75: 'int', 76: 'int', 77: 'int', 78: 'int', 79: 'int', 80: 'int',
                                  81: 'int',
                                  82: 'int', 83: 'int', 84: 'int', 85: 'int', 86: 'int', 87: 'float', 88: 'float',
                                  89: 'int',
                                  90: 'int', 91: 'int', 92: 'int', 93: 'int', 94: 'int', 95: 'int', 96: 'int',
                                  97: 'int',
                                  98: 'int', 99: 'int', 100: 'int', 101: 'int', 102: 'int', 103: 'int', 104: 'int',
                                  105: 'int',
                                  106: 'int', 107: 'int', 108: 'int', 109: 'int', 110: 'int', 111: 'int', 112: 'int',
                                  113: 'int', 114: 'int', 115: 'int', 116: 'int', 117: 'int', 118: 'int', 119: 'int',
                                  120: 'int', 121: 'int', 122: 'int', 123: 'int', 124: 'int', 125: 'int', 126: 'int',
                                  127: 'int', 128: 'int', 129: 'int', 130: 'int', 131: 'int', 132: 'int', 133: 'int',
                                  134: 'int', 135: 'int', 136: 'int', 137: 'int', 138: 'int', 139: 'int', 140: 'int',
                                  141: 'int', 142: 'int', 143: 'int', 144: 'int', 145: 'int', 146: 'int', 147: 'int',
                                  148: 'float', 149: 'float', 150: 'float', 151: 'float',
                                  152: 'int', 153: 'int'}
        self.metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate',
                                   4: 'avg_retransmission_timeout_value',
                                   5: 'byte_ack', 6: 'seg_out', 7: 'retrans', 8: 'mss_value', 9: 'ssthresh_value',
                                   10: 'segs_in', 11: 'avg_send_value', 12: 'unacked_value', 13: 'rcv_space',
                                   14: 'send_buffer_value', 15: 'read_req', 16: 'write_req', 17: 'rkB', 18: 'wkB',
                                   19: 'rrqm',
                                   20: 'wrqm', 21: 'rrqm_perc', 22: 'wrqm_perc', 23: 'r_await', 24: 'w_await',
                                   25: 'aqu_sz',
                                   26: 'rareq_sz', 27: 'wareq_sz', 28: 'svctm', 29: 'util', 30: 'rchar', 31: 'wchar',
                                   32: 'syscr', 33: 'syscw', 34: 'read_bytes_io', 35: 'write_bytes_io',
                                   36: 'cancelled_write_bytes', 37: 'pid', 38: 'ppid', 39: 'pgrp', 40: 'session',
                                   41: 'tty_nr',
                                   42: 'tpgid', 43: 'flags', 44: 'minflt', 45: 'cminflt', 46: 'majflt', 47: 'cmajflt',
                                   48: 'utime', 49: 'stime', 50: 'cutime', 51: 'cstime', 52: 'priority', 53: 'nice',
                                   54: 'num_threads', 55: 'itrealvalue', 56: 'starttime', 57: 'vsize', 58: 'rss',
                                   59: 'rsslim',
                                   60: 'startcode', 61: 'endcode', 62: 'startstack', 63: 'kstkesp', 64: 'kstkeip',
                                   65: 'signal',
                                   66: 'blocked', 67: 'sigignore', 68: 'sigcatch', 69: 'wchan', 70: 'nswap',
                                   71: 'cnswap',
                                   72: 'exit_signal', 73: 'processor', 74: 'rt_priority', 75: 'policy',
                                   76: 'delayacct_blkio_ticks', 77: 'guest_time', 78: 'cguest_time', 79: 'start_data',
                                   80: 'end_data', 81: 'start_brk', 82: 'arg_start', 83: 'arg_end', 84: 'env_start',
                                   85: 'env_end', 86: 'exit_code', 87: 'cpu_usage_percentage',
                                   88: 'mem_usage_percentage',
                                   89: 'tcp_rcv_buffer_min', 90: 'tcp_rcv_buffer_default', 91: 'tcp_rcv_buffer_max',
                                   92: 'tcp_snd_buffer_min', 93: 'tcp_snd_buffer_default', 94: 'tcp_snd_buffer_max',

                                   95: 'req_waittime', 96: 'req_active', 97: 'read_bytes', 98: 'write_bytes',
                                   99: 'ost_setattr',
                                   100: 'ost_read', 101: 'ost_write', 102: 'ost_get_info', 103: 'ost_connect',
                                   104: 'ost_punch',
                                   105: 'ost_statfs', 106: 'ost_sync', 107: 'ost_quotactl', 108: 'ldlm_cancel',
                                   109: 'obd_ping',

                                   110: 'pending_read_pages', 111: 'read_RPCs_in_flight', 112: 'avg_waittime_md',
                                   113: 'inflight_md', 114: 'unregistering_md', 115: 'timeouts_md',
                                   116: 'req_waittime_md',
                                   117: 'req_active_md', 118: 'mds_getattr_md', 119: 'mds_getattr_lock_md',
                                   120: 'mds_close_md', 121: 'mds_readpage_md', 122: 'mds_connect_md',
                                   123: 'mds_get_root_md', 124: 'mds_statfs_md', 125: 'mds_sync_md',
                                   126: 'mds_quotactl_md',
                                   127: 'mds_getxattr_md', 128: 'mds_hsm_state_set_md', 129: 'ldlm_cancel_md',
                                   130: 'obd_ping_md', 131: 'seq_query_md', 132: 'fld_query_md', 133: 'close_md',
                                   134: 'create_md', 135: 'enqueue_md', 136: 'getattr_md', 137: 'intent_lock_md',
                                   138: 'link_md', 139: 'rename_md', 140: 'setattr_md', 141: 'fsync_md',
                                   142: 'read_page_md', 143: 'unlink_md', 144: 'setxattr_md', 145: 'getxattr_md',
                                   146: 'intent_getattr_async_md', 147: 'revalidate_lock_md',
                                   148: 'avg_dsack_dups_value', 149: 'avg_reord_seen',
                                   150: 'system_cpu_percent', 151: 'system_memory_percent',
                                   152: 'remote_ost_read_bytes', 153: 'remote_ost_write_bytes'}
        self.log_id_to_attr = {1: 'time_stamp',  4: 'label_value'}
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

    def _is_number(self, string_):
        try:
            complex(string_)  # for int, long, float and complex
        except ValueError:
            return False
        return True

    def _get_mbps(self, thpt):
        if self._is_number(thpt):
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

    def _get_data_type(self, val, type_):
        if type_ == "string":
            return float(self._get_mbps(val))
        elif type_ == "float":
            return float(val)
        elif type_ == "intonly":
            tmp_value = str(val).split(".")[0]
            return int(tmp_value)
        elif type_ == "dict":
            pass
        else:
            return int(float(val))

    def data_str_to_json(self, data_str):
        data_str = data_str.strip("\n")
        row = data_str.split(",")
        new_row_json = {}
        # row[0]
        type_ = self.log_data_types[1]
        new_row_json[self.log_id_to_attr[1]] = self._get_data_type(row[0], type_)
        # row[1:139]
        total_keys_number = len(self.keys)
        for i in range(total_keys_number):
            type_ = self.metrics_datatypes[self.keys[i]]
            new_row_json["{}{}".format(self.prefix, self.metrics_id_to_attr[self.keys[i]])] = self._get_data_type(row[i+1],
                                                                                                                  type_)
        # row[-1]
        type_ = self.log_data_types[4]
        new_row_json[self.log_id_to_attr[4]] = self._get_data_type(row[-1], type_)
        return new_row_json