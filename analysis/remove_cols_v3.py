import pandas as pd
from collections import Counter

general_metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate',
                              4: 'avg_retransmission_timeout_value',
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
                              72: 'env_end', 73: 'exit_code',

                              74: 'cpu_usage_percentage', 75: 'mem_usage_percentage',

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

                              137: 'nic_send_bytes', 138: 'nic_receive_bytes',

                              139: 'remote_ost_read_bytes', 140: 'remote_ost_write_bytes',

                              141: 'dtn_lustre_read_bytes', 142: 'dtn_lustre_write_bytes', }

sender_keys = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16] + list(range(17, 23)) + [41, 44, 45] + list(range(74, 99)) + \
              [99, 100, 103, 104, 105, 106, 107, 108, 116, 117, 120, 121, 124, 127, 129, 130] + list(range(135, 143))

receiver_keys = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16] + list(range(17, 23)) + [41, 44, 45] + list(range(74, 99)) + \
              [99, 100, 103, 104, 105, 106, 107, 108, 116, 117, 120, 121, 124, 127, 129, 130] + list(range(135, 143))

class GroupedLabels:
    def __init__(self):
        self.label_to_error = {0: "normal",
                               1: "read", 2: "read", 3: "read",
                               4: "write", 5: "write", 6: "write",
                               7: "read_link", 8: "read_link", 9: "read_link",
                               10: "write_link", 11: "write_link", 12: "write_link",
                               13: "network", 14: "network", 15: "network", 16: "network",
                               17: "network", 18: "network", 19: "network", 20: "network",
                               21: "network", 22: "network", 23: "network", 24: "network",
                               25: "network", 26: "network", 27: "network", 28: "network",
                               29: "network", 30: "network", 31: "network", 32: "network",
                               33: "network", 34: "network", 35: "network", 36: "network",
                               37: "network", 38: "network", 39: "network", 40: "network", 41: "network", 42: "network",
                               43: "network", 44: "network", 45: "network", 46: "network", 47: "network", 48: "network",
                               }
        self.label_to_cate = {0: 0,
                              1: 1, 2: 1, 3: 1,
                              4: 2, 5: 2, 6: 2,
                              7: 3, 8: 3, 9: 3,
                              10: 4, 11: 5, 12: 4,
                              13: 5, 14: 5, 15: 5, 16: 5,
                              17: 5, 18: 5, 19: 5, 20: 5,
                              21: 5, 22: 5, 23: 5, 24: 5,
                              25: 5, 26: 5, 27: 5, 28: 5,
                              29: 5, 30: 5, 31: 5, 32: 5,
                              33: 5, 34: 5, 35: 5, 36: 5,
                              37: 5, 38: 5, 39: 5, 40: 5, 41: 5, 42: 5,
                              43: 5, 44: 5, 45: 5, 46: 5, 47: 5, 48: 5}

    def grouped_levels_cate_v2(self, df, total_possible_labels):
        aggregated_labels = {}
        for i in range(total_possible_labels + 1):
            aggregated_labels[i] = i
        # 0 is normal and is one group itself
        # group read congestion levels together
        for i in range(1, 4):
            aggregated_labels.update({i: 1})
        # group write congestion levels together
        for i in range(4, 7):
            aggregated_labels.update({i: 4})
        # group read link congestion levels together
        for i in range(7, 10):
            aggregated_labels.update({i: 7})
        # group write link congestion levels together
        for i in range(10, 13):
            aggregated_labels.update({i: 10})
        # group network loss levels
        for i in range(13, 17):
            aggregated_labels.update({i: 13})
        # group jitter
        for i in range(17, 21):
            aggregated_labels.update({i: 17})
        # group network duplicate
        for i in range(21, 25):
            aggregated_labels.update({i: 21})
        # group network corrupt
        for i in range(25, 29):
            aggregated_labels.update({i: 25})
        # group network reorder
        for i in range(29, 33):
            aggregated_labels.update({i: 29})
        # group network congestion
        for i in range(33, 37):
            aggregated_labels.update({i: 33})
        # group send buffer value
        for i in range(37, 43):
            aggregated_labels.update({i: 37})
        # group receive buffer value
        for i in range(43, 49):
            aggregated_labels.update({i: 43})

        y = [aggregated_labels[int(i)] for i in df[df.columns[len(df.columns) - 1]].values]
        df["label_value"] = y
        return df

# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsine-220g2-10Gbps_ssd_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsin_c220g1-10Gbps_hdd_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/utah-6525-25g-25Gbps_ssd_unmerged_all_cols_V3.csv")
unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsine-220g2-10Gbps_hdd_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/utah-6525-25-ssd-delayed-30ms_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsine-220g2-hdd-ssd_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsin-220g2-ssd-delayed-10ms_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/utah-6525-25-ssd-delayed-10ms_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsin-220g2-hdd-delayed-10ms_unmerged_all_cols_V3.csv")
# unmerged_all_cols = pd.read_csv("../csv_to_protobuf_bin/dataframe_logs/CLOUDLAB/wisconsin-220g2-ssd-simultanious-v2_unmerged_all_cols_V3.csv")

print(unmerged_all_cols.shape)
print(len(dict(Counter(unmerged_all_cols[unmerged_all_cols.columns[len(unmerged_all_cols.columns) - 1]]))), "labels")

# SELECTING COLs
selected_cols_names = ['time_stamp']
for skey in sender_keys:
    selected_cols_names.append("sender_{}".format(general_metrics_id_to_attr[skey]))
for rkey in receiver_keys:
    selected_cols_names.append("receiver_{}".format(general_metrics_id_to_attr[rkey]))
selected_cols_names += ['through_put', 'label_value']

unmerged_removed_cols = unmerged_all_cols.copy(deep=True)
unmerged_removed_cols = unmerged_removed_cols[selected_cols_names]
print(unmerged_removed_cols.shape)
print(len(dict(Counter(unmerged_removed_cols[unmerged_removed_cols.columns[len(unmerged_removed_cols.columns) - 1]]))), "labels")

# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-10Gbps_ssd_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/utah-6525-25g-25Gbps_ssd_unmerged_V3.csv", index=False)
unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-10Gbps_hdd_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/utah-6525-25-ssd-delayed-30ms_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-hdd-ssd_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-ssd-delayed-10ms_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/utah-6525-25-ssd-delayed-10ms_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-hdd-delayed-10ms_unmerged_V3.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/ds/v3/selected_cols/wisconsin-220g2-ssd-simultanious-v2.csv", index=False)

merged_removed_cols = unmerged_removed_cols.copy(deep=True)
g_label = GroupedLabels()
merged_removed_cols = g_label.grouped_levels_cate_v2(merged_removed_cols, 49)
print(merged_removed_cols.shape)
print(len(dict(Counter(merged_removed_cols[merged_removed_cols.columns[len(merged_removed_cols.columns) - 1]]))))
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/wisconsin-220g2-10Gbps_ssd_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/utah-6525-25g-25Gbps_ssd_merged.csv", index=False)
merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/wisconsin-220g2-10Gbps_hdd_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/utah-6525-25-ssd-delayed-30ms_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/wisconsin-220g2-hdd-ssd_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/wisconsin-220g2-ssd-delayed-10ms_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/utah-6525-25-ssd-delayed-10ms_merged_V3.csv", index=False)
# merged_removed_cols.to_csv("../prototype/ds/v3/selected_cols_merged/wisconsin-220g2-hdd-delayed-10ms_merged_V3.csv", index=False)
