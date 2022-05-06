import pandas as pd
from analysis_classes import GroupedLabels


general_metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate',
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


sender_keys = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14] + list(range(30, 37)) + [54, 57, 58] + \
                   [87, 88, 92, 94, 95, 96, 97, 98, 99, 100, 101, 104, 108] + \
                   [110, 111, 112, 113, 116, 117, 119, 120, 121, 129, 130, 133, 134, 137, 140, 142, 143] + \
                   [148, 149, 150, 151, 152, 153]

receiver_keys = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14] + list(range(30, 37)) + [54, 57, 58] + \
                     [87, 88, 92, 94, 95, 96, 97, 98, 99, 100, 101, 104, 108] + \
                     [110, 111, 112, 113, 116, 117, 119, 120, 121, 129, 130, 133, 134, 137, 140, 142, 143] + \
                     [148, 149, 150, 151, 152, 153]

from collections import Counter

# unmerged_all_cols = pd.read_csv("../prototype/ds/emulab_d460_10Gbps_hdd_unmerged_all_cols_V2.csv")
# unmerged_all_cols = pd.read_csv("../prototype/ds/utah_c6525-25g_25Gbps_ssd_unmerged_all_cols_V2.csv")
# unmerged_all_cols = pd.read_csv("../prototype/ds/wisconsin_c220g1-10Gbps_ssd_unmerged_all_cols_V2.csv")
unmerged_all_cols = pd.read_csv("../prototype/ds/utah_c6525-25g_1Gbps_ssd_unmerged_all_cols_V2.csv")
# unmerged_all_cols = pd.read_csv("../prototype/ds/wisconsin_c220g1-10Gbps_hdd_ssd_unmerged_all_cols_V2.csv")
print(unmerged_all_cols.shape)
print(len(dict(Counter(unmerged_all_cols[unmerged_all_cols.columns[len(unmerged_all_cols.columns) - 1]]))), "labels")

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
# unmerged_removed_cols.to_csv("../prototype/emulab_d460_10Gbps_hdd_unmerged_V2.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/utah_c6525-25g_25Gbps_ssd_unmerged_V2.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/wisconsin_c220g1-10Gbps_ssd_unmerged_V2.csv", index=False)
unmerged_removed_cols.to_csv("../prototype/utah_c6525-25g_1Gbps_ssd_unmerged_V2.csv", index=False)
# unmerged_removed_cols.to_csv("../prototype/wisconsin_c220g1-10Gbps_hdd_ssd_unmerged_V2.csv", index=False)


merged_removed_cols = unmerged_removed_cols.copy(deep=True)
g_label = GroupedLabels(total_possible_labels=0)
merged_removed_cols = g_label.grouped_levels_cate_v2(merged_removed_cols, 157)
print(merged_removed_cols.shape)
print(len(dict(Counter(merged_removed_cols[merged_removed_cols.columns[len(merged_removed_cols.columns) - 1]]))))
# merged_removed_cols.to_csv("../prototype/emulab_d460_10Gbps_hdd_merged_V2.csv", index=False)
# merged_removed_cols.to_csv("../prototype/utah_c6525-25g_25Gbps_ssd_merged_V2.csv", index=False)
# merged_removed_cols.to_csv("../prototype/wisconsin_c220g1-10Gbps_ssd_merged_V2.csv", index=False)
merged_removed_cols.to_csv("../prototype/utah_c6525-25g_1Gbps_ssd_merged_V2.csv", index=False)
# merged_removed_cols.to_csv("../prototype/wisconsin_c220g1-10Gbps_hdd_ssd_merged_V2.csv", index=False)
