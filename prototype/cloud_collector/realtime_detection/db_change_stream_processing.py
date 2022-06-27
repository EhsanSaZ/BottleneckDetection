import traceback

import pandas as pd
import pymongo


def db_change_stream_process(db_connection, db_name, transfer_id):
    print(transfer_id)
    logs_collection = db_connection[db_name]["logs"]
    sender_pipeline = [
        {'$match': {'operationType': 'insert', 'fullDocument.transfer_ID': transfer_id,
                    'fullDocument.is_sender': 1}}]
    receiver_pipeline = [
        {'$match': {'operationType': 'insert', 'fullDocument.transfer_ID': transfer_id,
                    'fullDocument.is_sender': 0}}]
    metrics_id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate', 4: 'avg_retransmission_timeout_value',
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
    selected_metrics = list(range(1, 15)) + list(range(30, 148)) + [148, 149, 150, 151, 152, 153]

    sender_get_next = True
    sender_resume_token = None
    receiver_get_next = True
    receiver_resume_token = None
    try:
        with logs_collection.watch(pipeline=sender_pipeline, resume_after=sender_resume_token) as sender_stream:
            with logs_collection.watch(pipeline=receiver_pipeline,
                                       resume_after=receiver_resume_token) as receiver_stream:
                while sender_stream.alive and receiver_stream.alive:
                    if sender_get_next:
                        sender_change = sender_stream.next()
                    sender_resume_token = sender_stream.resume_token
                    if receiver_get_next:
                        receiver_change = receiver_stream.next()
                        receiver_resume_token = receiver_stream.resume_token
                    sender_time = sender_change["fullDocument"]["time_stamp_sec"]
                    receiver_time = receiver_change["fullDocument"]["time_stamp_sec"]
                    if sender_time == receiver_time:
                        # There is a match and match these two updates and do the prediction
                        sender_data = sender_change["fullDocument"]["data"]
                        receiver_data = receiver_change["fullDocument"]["data"]
                        cols = []
                        data = []
                        for i in selected_metrics:
                            metric_name = metrics_id_to_attr[i]
                            key = "sender_{}".format(metric_name)
                            cols.append(key)
                            data.append(sender_data[key])
                        for i in selected_metrics:
                            metric_name = metrics_id_to_attr[i]
                            key = "receiver_{}".format(metric_name)
                            cols.append(key)
                            data.append(receiver_data[key])
                        df = pd.DataFrame([data], columns=cols)
                        # print(df)
                        print("sender, receiver", sender_change["fullDocument"]["time_stamp_sec"], sender_change["fullDocument"]["transfer_ID"])
                        # print("receiver", receiver_change["fullDocument"]["time_stamp_sec"], receiver_change["fullDocument"]["transfer_ID"] )
                        sender_get_next = True
                        receiver_get_next = True
                    elif sender_time > receiver_time:
                        # check for the next data from receiver
                        sender_get_next = False
                        receiver_get_next = True
                    else:
                        # receiver_time is > sender_time
                        # check for the next log from sender
                        sender_get_next = True
                        receiver_get_next = False
    except pymongo.errors.PyMongoError as e:
        if sender_resume_token is None or receiver_resume_token:
            traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
