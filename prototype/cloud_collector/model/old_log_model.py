import datetime
import traceback

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# from mongoengine import *
#
# connection = connect('testdb', host='mongodb://localhost:27017/testdb', username='mongoadmin', password='mongoadmin')
# l = connection.get_database('testdb').list_collection_names()
# print(l)
#
#
# class MonitoringLog(DynamicDocument):
#     avg_rtt_value = FloatField()
#     pacing_rate = StringField()
#     cwnd_rate = FloatField()
#     avg_retransmission_timeout_value = FloatField()
#     byte_ack = FloatField()
#     seg_out = FloatField()
#     retrans = FloatField()
#     mss_value = FloatField()
#     ssthresh_value = FloatField()
#     segs_in = FloatField()
#     avg_send_value = StringField()
#     unacked_value = FloatField()
#     rcv_space = FloatField()
#     send_buffer_value = FloatField()
#     read_req = FloatField()
#     write_req = FloatField()
#     rkB = FloatField()
#     wkB = FloatField()
#     rrqm = FloatField()
#     wrqm = FloatField()
#     rrqm_perc = FloatField()
#     wrqm_perc = FloatField()
#     r_await = FloatField()
#     w_await = FloatField()
#     aqu_sz = FloatField()
#     rareq_sz = FloatField()
#     wareq_sz = FloatField()
#     svctm = FloatField()
#     util = FloatField()
#     rchar = FloatField()
#     wchar = FloatField()
#     syscr = FloatField()
#     syscw = FloatField()
#     read_bytes_io = FloatField()
#     write_bytes_io = FloatField()
#     cancelled_write_bytes = FloatField()
#     pid = FloatField()
#     ppid = FloatField()
#     pgrp = FloatField()
#     session = FloatField()
#     tty_nr = FloatField()
#     tpgid = FloatField()
#     flags = FloatField()
#     minflt = FloatField()
#     cminflt = FloatField()
#     majflt = FloatField()
#     cmajflt = FloatField()
#     utime = FloatField()
#     stime = FloatField()
#     cutime = FloatField()
#     cstime = FloatField()
#     priority = FloatField()
#     nice = FloatField()
#     num_threads = FloatField()
#     itrealvalue = FloatField()
#     starttime = FloatField()
#     vsize = FloatField()
#     rss = FloatField()
#     rsslim = FloatField()
#     startcode = FloatField()
#     endcode = FloatField()
#     startstack = FloatField()
#     kstkesp = FloatField()
#     kstkeip = FloatField()
#     signal = FloatField()
#     blocked = FloatField()
#     sigignore = FloatField()
#     sigcatch = FloatField()
#     wchan = FloatField()
#     nswap = FloatField()
#     cnswap = FloatField()
#     exit_signal = FloatField()
#     processor = FloatField()
#     rt_priority = FloatField()
#     policy = FloatField()
#     delayacct_blkio_ticks = FloatField()
#     guest_time = FloatField()
#     cguest_time = FloatField()
#     start_data = FloatField()
#     end_data = FloatField()
#     start_brk = FloatField()
#     arg_start = FloatField()
#     arg_end = FloatField()
#     env_start = FloatField()
#     env_end = FloatField()
#     exit_code = FloatField()
#     cpu_usage_percentage = FloatField()
#     mem_usage_percentage = FloatField()
#     tcp_rcv_buffer_min = FloatField()
#     tcp_rcv_buffer_default = FloatField()
#     tcp_rcv_buffer_max = FloatField()
#     tcp_snd_buffer_min = FloatField()
#     tcp_snd_buffer_default = FloatField()
#     tcp_snd_buffer_max = FloatField()
#     req_waittime = FloatField()
#     req_active = FloatField()
#     read_bytes = FloatField()
#     write_bytes = FloatField()
#     ost_setattr = FloatField()
#     ost_read = FloatField()
#     ost_write = FloatField()
#     ost_get_info = FloatField()
#     ost_connect = FloatField()
#     ost_punch = FloatField()
#     ost_statfs = FloatField()
#     ost_sync = FloatField()
#     ost_quotactl = FloatField()
#     ldlm_cancel = FloatField()
#     obd_ping = FloatField()
#     pending_read_pages = FloatField()
#     read_RPCs_in_flight = FloatField()
#     avg_waittime_md = FloatField()
#     inflight_md = FloatField()
#     unregistering_md = FloatField()
#     timeouts_md = FloatField()
#     req_waittime_md = FloatField()
#     req_active_md = FloatField()
#     mds_getattr_md = FloatField()
#     mds_getattr_lock_md = FloatField()
#     mds_close_md = FloatField()
#     mds_readpage_md = FloatField()
#     mds_connect_md = FloatField()
#     mds_get_root_md = FloatField()
#     mds_statfs_md = FloatField()
#     mds_sync_md = FloatField()
#     mds_quotactl_md = FloatField()
#     mds_getxattr_md = FloatField()
#     mds_hsm_state_set_md = FloatField()
#     ldlm_cancel_md = FloatField()
#     obd_ping_md = FloatField()
#     seq_query_md = FloatField()
#     fld_query_md = FloatField()
#     close_md = FloatField()
#     create_md = FloatField()
#     enqueue_md = FloatField()
#     getattr_md = FloatField()
#     intent_lock_md = FloatField()
#     link_md = FloatField()
#     rename_md = FloatField()
#     setattr_md = FloatField()
#     fsync_md = FloatField()
#     read_page_md = FloatField()
#     unlink_md = FloatField()
#     setxattr_md = FloatField()
#     getxattr_md = FloatField()
#     intent_getattr_async_md = FloatField()
#     revalidate_lock_md = FloatField()
#     avg_dsack_dups_value = FloatField()
#     avg_reord_seen = FloatField()
#     system_cpu_percent = FloatField()
#     system_memory_percent = FloatField()
#     remote_ost_read_bytes = FloatField()
#     remote_ost_write_bytes = FloatField()


client = MongoClient('mongodb://localhost:27017/testdb',
                     username='mongoadmin',
                     password='mongoadmin', )
try:
    # print(client.server_info())
    #     post = {"author": "Mike",
    #             "text": "My first blog post!",
    #             "tags": ["mongodb", "python", "pymongo"],
    #             "nest_data" :{
    #                 "f1":1,
    #                 "f2":2
    #             },
    #             "date": datetime.datetime.utcnow()}
    log = {"transfer_ID": None,
           "data": {'time_stamp': 1655240678.9673095, 'sender_avg_rtt_value': '30.351', 'sender_pacing_rate': '47.5',
                    'sender_cwnd_rate': '8317.0', 'sender_avg_retransmission_timeout_value': '231.0',
                    'sender_byte_ack': '419.9829511642456', 'sender_seg_out': '51093.0', 'sender_retrans': '0.0',
                    'sender_mss_value': '8948.0', 'sender_ssthresh_value': '0.0', 'sender_segs_in': '1994.0',
                    'sender_avg_send_value': '19616.0', 'sender_unacked_value': '1875.0', 'sender_rcv_space': '26880.0',
                    'sender_send_buffer_value': '16777216.0', 'sender_rchar': '437453333', 'sender_wchar': '184',
                    'sender_syscr': '3790', 'sender_syscw': '13', 'sender_read_bytes_io': '494927872',
                    'sender_write_bytes_io': '32768', 'sender_cancelled_write_bytes': '0', 'sender_pid': '18022',
                    'sender_ppid': '18017', 'sender_pgrp': '18017', 'sender_session': '17754', 'sender_tty_nr': '34816',
                    'sender_tpgid': '18017', 'sender_flags': '1077944320', 'sender_minflt': '25005',
                    'sender_cminflt': '157',
                    'sender_majflt': '0', 'sender_cmajflt': '0', 'sender_utime': '168', 'sender_stime': '28',
                    'sender_cutime': '0',
                    'sender_cstime': '0', 'sender_priority': '20', 'sender_nice': '0', 'sender_num_threads': '20',
                    'sender_itrealvalue': '0', 'sender_starttime': '70174921', 'sender_vsize': '36698910720',
                    'sender_rss': '32860',
                    'sender_rsslim': '18446744073709551615', 'sender_startcode': '94275939115008',
                    'sender_endcode': '94275939119060',
                    'sender_startstack': '140724175682352', 'sender_kstkesp': '140724175664800',
                    'sender_kstkeip': '140016654356439',
                    'sender_signal': '0', 'sender_blocked': '0', 'sender_sigignore': '0', 'sender_sigcatch': '16800975',
                    'sender_wchan': '1.8446744073709552e+19', 'sender_nswap': '0', 'sender_cnswap': '0',
                    'sender_exit_signal': '17',
                    'sender_processor': '27', 'sender_rt_priority': '0', 'sender_policy': '0',
                    'sender_delayacct_blkio_ticks': '0',
                    'sender_guest_time': '0', 'sender_cguest_time': '0', 'sender_start_data': '94275941219560',
                    'sender_end_data': '94275941220368', 'sender_start_brk': '94275945578496',
                    'sender_arg_start': '140724175685186',
                    'sender_arg_end': '140724175685317', 'sender_env_start': '140724175685317',
                    'sender_env_end': '140724175687662',
                    'sender_exit_code': '0', 'sender_cpu_usage_percentage': '26.8',
                    'sender_mem_usage_percentage': '0.09981026330166155', 'sender_tcp_rcv_buffer_min': '10240',
                    'sender_tcp_rcv_buffer_default': '87380', 'sender_tcp_rcv_buffer_max': '67108864',
                    'sender_tcp_snd_buffer_min': '10240', 'sender_tcp_snd_buffer_default': '87380',
                    'sender_tcp_snd_buffer_max': '67108864', 'sender_req_waittime': '5688943',
                    'sender_req_active': '826',
                    'sender_read_bytes': '444596224', 'sender_write_bytes': '0', 'sender_ost_setattr': '0',
                    'sender_ost_read': '5688943', 'sender_ost_write': '0', 'sender_ost_get_info': '0',
                    'sender_ost_connect': '0',
                    'sender_ost_punch': '0', 'sender_ost_statfs': '0', 'sender_ost_sync': '0',
                    'sender_ost_quotactl': '0',
                    'sender_ldlm_cancel': '0', 'sender_obd_ping': '0', 'sender_pending_read_pages': '9',
                    'sender_read_RPCs_in_flight': '6144', 'sender_avg_waittime_md': '235', 'sender_inflight_md': '0',
                    'sender_unregistering_md': '0', 'sender_timeouts_md': '0', 'sender_req_waittime_md': '1163',
                    'sender_req_active_md': '5', 'sender_mds_getattr_md': '0', 'sender_mds_getattr_lock_md': '218',
                    'sender_mds_close_md': '292', 'sender_mds_readpage_md': '0', 'sender_mds_connect_md': '0',
                    'sender_mds_get_root_md': '0', 'sender_mds_statfs_md': '0', 'sender_mds_sync_md': '0',
                    'sender_mds_quotactl_md': '0', 'sender_mds_getxattr_md': '0', 'sender_mds_hsm_state_set_md': '0',
                    'sender_ldlm_cancel_md': '0', 'sender_obd_ping_md': '0', 'sender_seq_query_md': '0',
                    'sender_fld_query_md': '0',
                    'sender_close_md': '2', 'sender_create_md': '0', 'sender_enqueue_md': '0', 'sender_getattr_md': '0',
                    'sender_intent_lock_md': '9', 'sender_link_md': '0', 'sender_rename_md': '0',
                    'sender_setattr_md': '0',
                    'sender_fsync_md': '0', 'sender_read_page_md': '0', 'sender_unlink_md': '0',
                    'sender_setxattr_md': '0',
                    'sender_getxattr_md': '0', 'sender_intent_getattr_async_md': '0', 'sender_revalidate_lock_md': '0',
                    'sender_avg_dsack_dups_value': '0.0', 'sender_avg_reord_seen': '0.0',
                    'sender_system_cpu_percent': '1.9',
                    'sender_system_memory_percent': '3.4', 'sender_remote_ost_read_bytes': '452984832',
                    'sender_remote_ost_write_bytes': '0', 'label_value': '9999'},
           "sequence_number": 1,
           "is_sender": 1
           }

    # log["time_stamp_in_sec"] = int(log["data"]["time_stamp"])
    logs = client["testdb"].senders_logs
    insert_id = logs.insert_one(log).inserted_id
    # s = "function(time_stamp) { return Math.trunc(time_stamp) =="+ str(int(1655240678.9673095))+" ; }"
    # l = logs.find_one({"data.time_stamp": 1655240678.9673095})
    # l = logs.find_one( {"$expr": { "$function": {
    #   "body": s,
    #   "args": [ "$data.time_stamp"],
    #   "lang": "js" } } } )

    # pipeline = [
    #     {
    #         "$addFields": {
    #             "time_in_sec": {
    #                 "$toInt": "$data.time_stamp"
    #             }
    #         }
    #     },
    #     {
    #         "$match": {
    #             "time_in_sec": {
    #                 "$eq": int(1655240678.9673095)
    #             }
    #         }
    #     }
    #
    # ]
    # results = logs.aggregate(pipeline)
    # print(results)
    # for doc in results:
    #     print(doc)

#     p = posts.find_one({"author": "Mike"})
#     print(p)
except Exception as e:
    print(traceback.format_exc())
    print(e)
    print("Unable to connect to the server.")

# from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Float, TIMESTAMP
#
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
#
#
# class MonitoringLog(Base):
#     # __tablename__ = "monitoring_log"
#     transfer_ID = Column(String(255), primary_key=True)
#     sequence_number = Column(Integer, primary_key=True)
#     is_sender = Column(Boolean, nullable=True)
#     time_stamp = Column(TIMESTAMP, nullable=True)
#
#     avg_rtt_value = Column(Float, nullable=True)
#     pacing_rate = Column(String(255), nullable=True)
#     cwnd_rate = Column(Float, nullable=True)
#     avg_retransmission_timeout_value = Column(Float, nullable=True)
#     byte_ack = Column(Float, nullable=True)
#     seg_out = Column(Float, nullable=True)
#     retrans = Column(Float, nullable=True)
#     mss_value = Column(Float, nullable=True)
#     ssthresh_value = Column(Float, nullable=True)
#     segs_in = Column(Float, nullable=True)
#     avg_send_value = Column(String(255), nullable=True)
#     unacked_value = Column(Float, nullable=True)
#     rcv_space = Column(Float, nullable=True)
#     send_buffer_value = Column(Float, nullable=True)
#     read_req = Column(Float, nullable=True)
#     write_req = Column(Float, nullable=True)
#     rkB = Column(Float, nullable=True)
#     wkB = Column(Float, nullable=True)
#     rrqm = Column(Float, nullable=True)
#     wrqm = Column(Float, nullable=True)
#     rrqm_perc = Column(Float, nullable=True)
#     wrqm_perc = Column(Float, nullable=True)
#     r_await = Column(Float, nullable=True)
#     w_await = Column(Float, nullable=True)
#     aqu_sz = Column(Float, nullable=True)
#     rareq_sz = Column(Float, nullable=True)
#     wareq_sz = Column(Float, nullable=True)
#     svctm = Column(Float, nullable=True)
#     util = Column(Float, nullable=True)
#     rchar = Column(Integer, nullable=True)
#     wchar = Column(Integer, nullable=True)
#     syscr = Column(Integer, nullable=True)
#     syscw = Column(Integer, nullable=True)
#     read_bytes_io = Column(Integer, nullable=True)
#     write_bytes_io = Column(Integer, nullable=True)
#     cancelled_write_bytes = Column(Integer, nullable=True)
#     pid = Column(Integer, nullable=True)
#     ppid = Column(Integer, nullable=True)
#     pgrp = Column(Integer, nullable=True)
#     session = Column(Integer, nullable=True)
#     tty_nr = Column(Integer, nullable=True)
#     tpgid = Column(Integer, nullable=True)
#     flags = Column(Integer, nullable=True)
#     minflt = Column(Integer, nullable=True)
#     cminflt = Column(Integer, nullable=True)
#     majflt = Column(Integer, nullable=True)
#     cmajflt = Column(Integer, nullable=True)
#     utime = Column(Integer, nullable=True)
#     stime = Column(Integer, nullable=True)
#     cutime = Column(Integer, nullable=True)
#     cstime = Column(Integer, nullable=True)
#     priority = Column(Integer, nullable=True)
#     nice = Column(Integer, nullable=True)
#     num_threads = Column(Integer, nullable=True)
#     itrealvalue = Column(Integer, nullable=True)
#     starttime = Column(Integer, nullable=True)
#     vsize = Column(Integer, nullable=True)
#     rss = Column(Integer, nullable=True)
#     rsslim = Column(Integer, nullable=True)
#     startcode = Column(Integer, nullable=True)
#     endcode = Column(Integer, nullable=True)
#     startstack = Column(Integer, nullable=True)
#     kstkesp = Column(Integer, nullable=True)
#     kstkeip = Column(Integer, nullable=True)
#     signal = Column(Integer, nullable=True)
#     blocked = Column(Integer, nullable=True)
#     sigignore = Column(Integer, nullable=True)
#     sigcatch = Column(Integer, nullable=True)
#     wchan = Column(Float, nullable=True)
#     nswap = Column(Integer, nullable=True)
#     cnswap = Column(Integer, nullable=True)
#     exit_signal = Column(Integer, nullable=True)
#     processor = Column(Integer, nullable=True)
#     rt_priority = Column(Integer, nullable=True)
#     policy = Column(Integer, nullable=True)
#     delayacct_blkio_ticks = Column(Integer, nullable=True)
#     guest_time = Column(Integer, nullable=True)
#     cguest_time = Column(Integer, nullable=True)
#     start_data = Column(Integer, nullable=True)
#     end_data = Column(Integer, nullable=True)
#     start_brk = Column(Integer, nullable=True)
#     arg_start = Column(Integer, nullable=True)
#     arg_end = Column(Integer, nullable=True)
#     env_start = Column(Integer, nullable=True)
#     env_end = Column(Integer, nullable=True)
#     exit_code = Column(Integer, nullable=True)
#     cpu_usage_percentage = Column(Float, nullable=True)
#     mem_usage_percentage = Column(Float, nullable=True)
#     tcp_rcv_buffer_min = Column(Integer, nullable=True)
#     tcp_rcv_buffer_default = Column(Integer, nullable=True)
#     tcp_rcv_buffer_max = Column(Integer, nullable=True)
#     tcp_snd_buffer_min = Column(Integer, nullable=True)
#     tcp_snd_buffer_default = Column(Integer, nullable=True)
#     tcp_snd_buffer_max = Column(Integer, nullable=True)
#     req_waittime = Column(Integer, nullable=True)
#     req_active = Column(Integer, nullable=True)
#     read_bytes = Column(Integer, nullable=True)
#     write_bytes = Column(Integer, nullable=True)
#     ost_setattr = Column(Integer, nullable=True)
#     ost_read = Column(Integer, nullable=True)
#     ost_write = Column(Integer, nullable=True)
#     ost_get_info = Column(Integer, nullable=True)
#     ost_connect = Column(Integer, nullable=True)
#     ost_punch = Column(Integer, nullable=True)
#     ost_statfs = Column(Integer, nullable=True)
#     ost_sync = Column(Integer, nullable=True)
#     ost_quotactl = Column(Integer, nullable=True)
#     ldlm_cancel = Column(Integer, nullable=True)
#     obd_ping = Column(Integer, nullable=True)
#     pending_read_pages = Column(Integer, nullable=True)
#     read_RPCs_in_flight = Column(Integer, nullable=True)
#     avg_waittime_md = Column(Integer, nullable=True)
#     inflight_md = Column(Integer, nullable=True)
#     unregistering_md = Column(Integer, nullable=True)
#     timeouts_md = Column(Integer, nullable=True)
#     req_waittime_md = Column(Integer, nullable=True)
#     req_active_md = Column(Integer, nullable=True)
#     mds_getattr_md = Column(Integer, nullable=True)
#     mds_getattr_lock_md = Column(Integer, nullable=True)
#     mds_close_md = Column(Integer, nullable=True)
#     mds_readpage_md = Column(Integer, nullable=True)
#     mds_connect_md = Column(Integer, nullable=True)
#     mds_get_root_md = Column(Integer, nullable=True)
#     mds_statfs_md = Column(Integer, nullable=True)
#     mds_sync_md = Column(Integer, nullable=True)
#     mds_quotactl_md = Column(Integer, nullable=True)
#     mds_getxattr_md = Column(Integer, nullable=True)
#     mds_hsm_state_set_md = Column(Integer, nullable=True)
#     ldlm_cancel_md = Column(Integer, nullable=True)
#     obd_ping_md = Column(Integer, nullable=True)
#     seq_query_md = Column(Integer, nullable=True)
#     fld_query_md = Column(Integer, nullable=True)
#     close_md = Column(Integer, nullable=True)
#     create_md = Column(Integer, nullable=True)
#     enqueue_md = Column(Integer, nullable=True)
#     getattr_md = Column(Integer, nullable=True)
#     intent_lock_md = Column(Integer, nullable=True)
#     link_md = Column(Integer, nullable=True)
#     rename_md = Column(Integer, nullable=True)
#     setattr_md = Column(Integer, nullable=True)
#     fsync_md = Column(Integer, nullable=True)
#     read_page_md = Column(Integer, nullable=True)
#     unlink_md = Column(Integer, nullable=True)
#     setxattr_md = Column(Integer, nullable=True)
#     getxattr_md = Column(Integer, nullable=True)
#     intent_getattr_async_md = Column(Integer, nullable=True)
#     revalidate_lock_md = Column(Integer, nullable=True)
#     avg_dsack_dups_value = Column(Float, nullable=True)
#     avg_reord_seen = Column(Float, nullable=True)
#     system_cpu_percent = Column(Float, nullable=True)
#     system_memory_percent = Column(Float, nullable=True)
#     remote_ost_read_bytes = Column(Integer, nullable=True)
#     remote_ost_write_bytes = Column(Integer, nullable=True)
