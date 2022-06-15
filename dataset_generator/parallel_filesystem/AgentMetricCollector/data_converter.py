import csv


class DataConverter:
    def __init__(self, file_system="normal", prefix=""):
        self.prefix = prefix
        self.file_system = file_system
        self.log_data_types = {1: 'float', 4: 'int'}
        self.metrics_datatypes = {1: 'string', 2: 'string', 3: 'string', 4: 'string', 5: 'string', 6: 'string', 7: 'string',
                                  8: 'string', 9: 'string', 10: 'string', 11: 'string', 12: 'string', 13: 'string',
                                  14: 'string',
                                  15: 'string', 16: 'string', 17: 'string', 18: 'string', 19: 'string', 20: 'string',
                                  21: 'string',
                                  22: 'string', 23: 'string', 24: 'string', 25: 'string', 26: 'string', 27: 'string',
                                  28: 'string',
                                  29: 'string', 30: 'string', 31: 'string', 32: 'string', 33: 'string', 34: 'string', 35: 'string',
                                  36: 'string',
                                  37: 'string', 38: 'string', 39: 'string', 40: 'string', 41: 'string', 42: 'string', 43: 'string',
                                  44: 'string',
                                  45: 'string', 46: 'string', 47: 'string', 48: 'string', 49: 'string', 50: 'string', 51: 'string',
                                  52: 'string',
                                  53: 'string', 54: 'string', 55: 'string', 56: 'string', 57: 'string', 58: 'string',
                                  59: 'intonly', 60: 'intonly', 61: 'intonly', 62: 'intonly', 63: 'string', 64: 'string',
                                  65: 'string',
                                  66: 'string', 67: 'string', 68: 'string', 69: 'string', 70: 'string', 71: 'string', 72: 'string',
                                  73: 'string',
                                  74: 'string', 75: 'string', 76: 'string', 77: 'string', 78: 'string', 79: 'string', 80: 'string',
                                  81: 'string',
                                  82: 'string', 83: 'string', 84: 'string', 85: 'string', 86: 'string', 87: 'string', 88: 'string',
                                  89: 'string',
                                  90: 'string', 91: 'string', 92: 'string', 93: 'string', 94: 'string', 95: 'string', 96: 'string',
                                  97: 'string',
                                  98: 'string', 99: 'string', 100: 'string', 101: 'string', 102: 'string', 103: 'string', 104: 'string',
                                  105: 'string',
                                  106: 'string', 107: 'string', 108: 'string', 109: 'string', 110: 'string', 111: 'string', 112: 'string',
                                  113: 'string', 114: 'string', 115: 'string', 116: 'string', 117: 'string', 118: 'string', 119: 'string',
                                  120: 'string', 121: 'string', 122: 'string', 123: 'string', 124: 'string', 125: 'string', 126: 'string',
                                  127: 'string', 128: 'string', 129: 'string', 130: 'string', 131: 'string', 132: 'string', 133: 'string',
                                  134: 'string', 135: 'string', 136: 'string', 137: 'string', 138: 'string', 139: 'string', 140: 'string',
                                  141: 'string', 142: 'string', 143: 'string', 144: 'string', 145: 'string', 146: 'string', 147: 'string',
                                  148: 'string', 149: 'string', 150: 'string', 151: 'string',
                                  152: 'string', 153: 'string'}
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
            return str(self._get_mbps(val))
        elif type_ == "float":
            return float(val)
        elif type_ == "intonly":
            tmp_value = str(val).split(".")[0]
            return str(tmp_value)
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