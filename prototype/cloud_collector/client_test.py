import concurrent
import json
import time
from concurrent.futures import ThreadPoolExecutor
import uuid
import copy
import zmq

context = zmq.Context()
host = "localhost"
port = "60000"

detector_host = "localhost"
detector_port = "50000"

ipc_path_name = "/tmp/zmqtest"
total_worker_processes = 3

# #  Socket to talk to server
# print("Connecting to hello world server...")
# socket = context.socket(zmq.REQ)
# socket.connect("tcp://{}:{}".format(host, port))
#
# socket.send_json({"request_type": "new_publisher_info",
#                   "data": {
#                       "sender": {
#                           "ip": "127.0.0.1",
#                           "port": "1111"
#                       },
#                       "receiver": {
#                           "ip": "127.0.0.1",
#                           "port": "2222"
#                       }
#                   }})
# message = socket.recv()
# print(f"Received reply [ {message} ]")
#
# socket2 = context.socket(zmq.PUB)
# socket2.bind("tcp://{}:{}".format("127.0.0.1", "1111"))
#
global_sender_payload = {"transfer_ID": 1,
                         "data": {'time_stamp': 1655240678.9673095, 'sender_avg_rtt_value': '30.351',
                                  'sender_pacing_rate': '47.5',
                                  'sender_cwnd_rate': '8317.0', 'sender_avg_retransmission_timeout_value': '231.0',
                                  'sender_byte_ack': '419.9829511642456', 'sender_seg_out': '51093.0',
                                  'sender_retrans': '0.0',
                                  'sender_mss_value': '8948.0', 'sender_ssthresh_value': '0.0',
                                  'sender_segs_in': '1994.0',
                                  'sender_avg_send_value': '19616.0', 'sender_unacked_value': '1875.0',
                                  'sender_rcv_space': '26880.0',
                                  'sender_send_buffer_value': '16777216.0', 'sender_rchar': '437453333',
                                  'sender_wchar': '184',
                                  'sender_syscr': '3790', 'sender_syscw': '13', 'sender_read_bytes_io': '494927872',
                                  'sender_write_bytes_io': '32768', 'sender_cancelled_write_bytes': '0',
                                  'sender_pid': '18022',
                                  'sender_ppid': '18017', 'sender_pgrp': '18017', 'sender_session': '17754',
                                  'sender_tty_nr': '34816',
                                  'sender_tpgid': '18017', 'sender_flags': '1077944320', 'sender_minflt': '25005',
                                  'sender_cminflt': '157',
                                  'sender_majflt': '0', 'sender_cmajflt': '0', 'sender_utime': '168',
                                  'sender_stime': '28',
                                  'sender_cutime': '0',
                                  'sender_cstime': '0', 'sender_priority': '20', 'sender_nice': '0',
                                  'sender_num_threads': '20',
                                  'sender_itrealvalue': '0', 'sender_starttime': '70174921',
                                  'sender_vsize': '36698910720',
                                  'sender_rss': '32860',
                                  'sender_rsslim': '18446744073709551615', 'sender_startcode': '94275939115008',
                                  'sender_endcode': '94275939119060',
                                  'sender_startstack': '140724175682352', 'sender_kstkesp': '140724175664800',
                                  'sender_kstkeip': '140016654356439',
                                  'sender_signal': '0', 'sender_blocked': '0', 'sender_sigignore': '0',
                                  'sender_sigcatch': '16800975',
                                  'sender_wchan': '1.8446744073709552e+19', 'sender_nswap': '0', 'sender_cnswap': '0',
                                  'sender_exit_signal': '17',
                                  'sender_processor': '27', 'sender_rt_priority': '0', 'sender_policy': '0',
                                  'sender_delayacct_blkio_ticks': '0',
                                  'sender_guest_time': '0', 'sender_cguest_time': '0',
                                  'sender_start_data': '94275941219560',
                                  'sender_end_data': '94275941220368', 'sender_start_brk': '94275945578496',
                                  'sender_arg_start': '140724175685186',
                                  'sender_arg_end': '140724175685317', 'sender_env_start': '140724175685317',
                                  'sender_env_end': '140724175687662',
                                  'sender_exit_code': '0', 'sender_cpu_usage_percentage': '26.8',
                                  'sender_mem_usage_percentage': '0.09981026330166155',
                                  'sender_tcp_rcv_buffer_min': '10240',
                                  'sender_tcp_rcv_buffer_default': '87380', 'sender_tcp_rcv_buffer_max': '67108864',
                                  'sender_tcp_snd_buffer_min': '10240', 'sender_tcp_snd_buffer_default': '87380',
                                  'sender_tcp_snd_buffer_max': '67108864', 'sender_req_waittime': '5688943',
                                  'sender_req_active': '826',
                                  'sender_read_bytes': '444596224', 'sender_write_bytes': '0',
                                  'sender_ost_setattr': '0',
                                  'sender_ost_read': '5688943', 'sender_ost_write': '0', 'sender_ost_get_info': '0',
                                  'sender_ost_connect': '0',
                                  'sender_ost_punch': '0', 'sender_ost_statfs': '0', 'sender_ost_sync': '0',
                                  'sender_ost_quotactl': '0',
                                  'sender_ldlm_cancel': '0', 'sender_obd_ping': '0', 'sender_pending_read_pages': '9',
                                  'sender_read_RPCs_in_flight': '6144', 'sender_avg_waittime_md': '235',
                                  'sender_inflight_md': '0',
                                  'sender_unregistering_md': '0', 'sender_timeouts_md': '0',
                                  'sender_req_waittime_md': '1163',
                                  'sender_req_active_md': '5', 'sender_mds_getattr_md': '0',
                                  'sender_mds_getattr_lock_md': '218',
                                  'sender_mds_close_md': '292', 'sender_mds_readpage_md': '0',
                                  'sender_mds_connect_md': '0',
                                  'sender_mds_get_root_md': '0', 'sender_mds_statfs_md': '0', 'sender_mds_sync_md': '0',
                                  'sender_mds_quotactl_md': '0', 'sender_mds_getxattr_md': '0',
                                  'sender_mds_hsm_state_set_md': '0',
                                  'sender_ldlm_cancel_md': '0', 'sender_obd_ping_md': '0', 'sender_seq_query_md': '0',
                                  'sender_fld_query_md': '0',
                                  'sender_close_md': '2', 'sender_create_md': '0', 'sender_enqueue_md': '0',
                                  'sender_getattr_md': '0',
                                  'sender_intent_lock_md': '9', 'sender_link_md': '0', 'sender_rename_md': '0',
                                  'sender_setattr_md': '0',
                                  'sender_fsync_md': '0', 'sender_read_page_md': '0', 'sender_unlink_md': '0',
                                  'sender_setxattr_md': '0',
                                  'sender_getxattr_md': '0', 'sender_intent_getattr_async_md': '0',
                                  'sender_revalidate_lock_md': '0',
                                  'sender_avg_dsack_dups_value': '0.0', 'sender_avg_reord_seen': '0.0',
                                  'sender_system_cpu_percent': '1.9',
                                  'sender_system_memory_percent': '3.4', 'sender_remote_ost_read_bytes': '452984832',
                                  'sender_remote_ost_write_bytes': '0', 'label_value': '9999'},
                         "sequence_number": 1,
                         "is_sender": 1
                         }
global_receiver_payload = {"transfer_ID": 1,
                           "data": {'time_stamp': 1655240678.9673095, 'receiver_avg_rtt_value': '30.351',
                                    'receiver_pacing_rate': '47.5',
                                    'receiver_cwnd_rate': '8317.0',
                                    'receiver_avg_retransmission_timeout_value': '231.0',
                                    'receiver_byte_ack': '419.9829511642456', 'receiver_seg_out': '51093.0',
                                    'receiver_retrans': '0.0',
                                    'receiver_mss_value': '8948.0', 'receiver_ssthresh_value': '0.0',
                                    'receiver_segs_in': '1994.0',
                                    'receiver_avg_send_value': '19616.0', 'receiver_unacked_value': '1875.0',
                                    'receiver_rcv_space': '26880.0',
                                    'receiver_send_buffer_value': '16777216.0', 'receiver_rchar': '437453333',
                                    'receiver_wchar': '184',
                                    'receiver_syscr': '3790', 'receiver_syscw': '13',
                                    'receiver_read_bytes_io': '494927872',
                                    'receiver_write_bytes_io': '32768', 'receiver_cancelled_write_bytes': '0',
                                    'receiver_pid': '18022',
                                    'receiver_ppid': '18017', 'receiver_pgrp': '18017', 'receiver_session': '17754',
                                    'receiver_tty_nr': '34816',
                                    'receiver_tpgid': '18017', 'receiver_flags': '1077944320',
                                    'receiver_minflt': '25005',
                                    'receiver_cminflt': '157',
                                    'receiver_majflt': '0', 'receiver_cmajflt': '0', 'receiver_utime': '168',
                                    'receiver_stime': '28',
                                    'receiver_cutime': '0',
                                    'receiver_cstime': '0', 'receiver_priority': '20', 'receiver_nice': '0',
                                    'receiver_num_threads': '20',
                                    'receiver_itrealvalue': '0', 'receiver_starttime': '70174921',
                                    'receiver_vsize': '36698910720',
                                    'receiver_rss': '32860',
                                    'receiver_rsslim': '18446744073709551615', 'receiver_startcode': '94275939115008',
                                    'receiver_endcode': '94275939119060',
                                    'receiver_startstack': '140724175682352', 'receiver_kstkesp': '140724175664800',
                                    'receiver_kstkeip': '140016654356439',
                                    'receiver_signal': '0', 'receiver_blocked': '0', 'receiver_sigignore': '0',
                                    'receiver_sigcatch': '16800975',
                                    'receiver_wchan': '1.8446744073709552e+19', 'receiver_nswap': '0',
                                    'receiver_cnswap': '0',
                                    'receiver_exit_signal': '17',
                                    'receiver_processor': '27', 'receiver_rt_priority': '0', 'receiver_policy': '0',
                                    'receiver_delayacct_blkio_ticks': '0',
                                    'receiver_guest_time': '0', 'receiver_cguest_time': '0',
                                    'receiver_start_data': '94275941219560',
                                    'receiver_end_data': '94275941220368', 'receiver_start_brk': '94275945578496',
                                    'receiver_arg_start': '140724175685186',
                                    'receiver_arg_end': '140724175685317', 'receiver_env_start': '140724175685317',
                                    'receiver_env_end': '140724175687662',
                                    'receiver_exit_code': '0', 'receiver_cpu_usage_percentage': '26.8',
                                    'receiver_mem_usage_percentage': '0.09981026330166155',
                                    'receiver_tcp_rcv_buffer_min': '10240',
                                    'receiver_tcp_rcv_buffer_default': '87380',
                                    'receiver_tcp_rcv_buffer_max': '67108864',
                                    'receiver_tcp_snd_buffer_min': '10240', 'receiver_tcp_snd_buffer_default': '87380',
                                    'receiver_tcp_snd_buffer_max': '67108864', 'receiver_req_waittime': '5688943',
                                    'receiver_req_active': '826',
                                    'receiver_read_bytes': '444596224', 'receiver_write_bytes': '0',
                                    'receiver_ost_setattr': '0',
                                    'receiver_ost_read': '5688943', 'receiver_ost_write': '0',
                                    'receiver_ost_get_info': '0',
                                    'receiver_ost_connect': '0',
                                    'receiver_ost_punch': '0', 'receiver_ost_statfs': '0', 'receiver_ost_sync': '0',
                                    'receiver_ost_quotactl': '0',
                                    'receiver_ldlm_cancel': '0', 'receiver_obd_ping': '0',
                                    'receiver_pending_read_pages': '9',
                                    'receiver_read_RPCs_in_flight': '6144', 'receiver_avg_waittime_md': '235',
                                    'receiver_inflight_md': '0',
                                    'receiver_unregistering_md': '0', 'receiver_timeouts_md': '0',
                                    'receiver_req_waittime_md': '1163',
                                    'receiver_req_active_md': '5', 'receiver_mds_getattr_md': '0',
                                    'receiver_mds_getattr_lock_md': '218',
                                    'receiver_mds_close_md': '292', 'receiver_mds_readpage_md': '0',
                                    'receiver_mds_connect_md': '0',
                                    'receiver_mds_get_root_md': '0', 'receiver_mds_statfs_md': '0',
                                    'receiver_mds_sync_md': '0',
                                    'receiver_mds_quotactl_md': '0', 'receiver_mds_getxattr_md': '0',
                                    'receiver_mds_hsm_state_set_md': '0',
                                    'receiver_ldlm_cancel_md': '0', 'receiver_obd_ping_md': '0',
                                    'receiver_seq_query_md': '0',
                                    'receiver_fld_query_md': '0',
                                    'receiver_close_md': '2', 'receiver_create_md': '0', 'receiver_enqueue_md': '0',
                                    'receiver_getattr_md': '0',
                                    'receiver_intent_lock_md': '9', 'receiver_link_md': '0', 'receiver_rename_md': '0',
                                    'receiver_setattr_md': '0',
                                    'receiver_fsync_md': '0', 'receiver_read_page_md': '0', 'receiver_unlink_md': '0',
                                    'receiver_setxattr_md': '0',
                                    'receiver_getxattr_md': '0', 'receiver_intent_getattr_async_md': '0',
                                    'receiver_revalidate_lock_md': '0',
                                    'receiver_avg_dsack_dups_value': '0.0', 'receiver_avg_reord_seen': '0.0',
                                    'receiver_system_cpu_percent': '1.9',
                                    'receiver_system_memory_percent': '3.4',
                                    'receiver_remote_ost_read_bytes': '452984832',
                                    'receiver_remote_ost_write_bytes': '0', 'label_value': '9999'},
                           "sequence_number": 1,
                           "is_sender": 1
                           }


# sequence_number = 1
# time_stamp = 1655240678.9673095
# transfer_ID = 1


# while (True):
#     payload["sequence_number"] = sequence_number
#     payload["data"]["time_stamp"] = time_stamp
#     socket2.send_json(payload)
#     time_stamp += 1
#     sequence_number += 1
#     time.sleep(1)
# #  Do 10 requests, waiting each time for a response
# for request in range(100000):
#     print(f"Sending request {request} ...")
#     socket.send_string("Hello")
# 
#     #  Get the reply.
#     message = socket.recv()
#     print(f"Received reply {request} [ {message} ]")
def sender_agent(sender_ip, sender_port, receiver_ip, receiver_port, transfer_id):
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{}:{}".format(host, port))
    # body = json.dumps()
    socket.send_json({"request_type": "new_publisher_info",
                      "data": {
                          "sender": {
                              "ip": sender_ip,
                              "port": sender_port
                          },
                          "receiver": {
                              "ip": receiver_ip,
                              "port": receiver_port
                          }
                      }})
    message = socket.recv()
    print(f"Received reply [ {message} ]")

    socket_sender_t_id = context.socket(zmq.REQ)
    socket_sender_t_id.connect("tcp://{}:{}".format(detector_host, detector_port))
    socket_sender_t_id.send_json({"request_type": "new_transfer", "data": {"transfer_id": transfer_id}})

    socket2 = context.socket(zmq.PUB)
    socket2.bind("tcp://{}:{}".format(sender_ip, sender_port))
    s_payload = copy.deepcopy(global_sender_payload)
    sequence_number = 1
    time_stamp = 1655240678.9673095
    transfer_ID = transfer_id
    while (True):
        s_payload["transfer_ID"] = transfer_ID
        s_payload["sequence_number"] = sequence_number
        s_payload["data"]["time_stamp"] = time_stamp
        body = json.dumps(s_payload)
        socket2.send_json(body)
        time_stamp += 1
        sequence_number += 1
        time.sleep(1)


def receiver_agent(sender_ip, sender_port, receiver_ip, receiver_port, transfer_id):
    socket2 = context.socket(zmq.PUB)
    socket2.bind("tcp://{}:{}".format(receiver_ip, receiver_port))
    r_payload = copy.deepcopy(global_receiver_payload)
    sequence_number = 1
    time_stamp = 1655240678.9673095
    transfer_ID = transfer_id
    while (True):
        r_payload["is_sender"] = 0
        r_payload["transfer_ID"] = transfer_ID
        r_payload["sequence_number"] = sequence_number
        r_payload["data"]["time_stamp"] = time_stamp
        body = json.dumps(r_payload)
        socket2.send_json(body)
        time_stamp += 1
        sequence_number += 1
        time.sleep(1)


with ThreadPoolExecutor(max_workers=100) as executor:
    sender_port = 1101
    receiver_port = 2201
    futures = []
    for i in range(1):
        u_id = uuid.uuid4()
        # u_id = 123
        # print(str(u_id))
        futures.append(
            executor.submit(sender_agent, "127.0.0.1", str(sender_port), "127.0.0.1", str(receiver_port), str(u_id)))
        futures.append(
            executor.submit(receiver_agent, "127.0.0.1", str(sender_port), "127.0.0.1", str(receiver_port), str(u_id)))
        sender_port += 1
        receiver_port += 1

    for future in concurrent.futures.as_completed(futures):
        print(future.result())
        # executor.submit(receiver_agent)
