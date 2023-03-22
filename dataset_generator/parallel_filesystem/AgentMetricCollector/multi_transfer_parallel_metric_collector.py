import argparse
import os
import time
from pathlib import Path
import psutil
import zmq

from Config import Config
from discovery.transfer_discovery import TransferDiscovery
from discovery.transfer_validation_strategy2 import TransferValidationStrategy_2
from transfer_manager import TransferManager
from helper_threads import globalMetricsMonitor
# from publisher import SendToCloud
from rabbitmq_publisher import SendToRabbit
from lustre_ost_metric_cache import LustreOstMetricCache
# from client_ost_metrics_cache import LustreClientOstMetricCache
from client_mdt_metrics_cache import LustreClientMdtMetricCache
from client_ost_metrics_shared_memory_cache import LustreClientOstMetricSharedMemCache
from client_mdt_metrics_shared_memory_cache import LustreClientMdtMetricSharedMemCache
from file_transfer_thread import  FileTransferThread
from run_server_thread import RunServerThread



# system_buffer_value_proto_message = BufferValueMetrics()
# system_buffer_value_proto_message.tcp_rcv_buffer_min = 0
# system_buffer_value_proto_message.tcp_rcv_buffer_default = 0
# system_buffer_value_proto_message.tcp_rcv_buffer_max = 0
# system_buffer_value_proto_message.tcp_snd_buffer_min = 0
# system_buffer_value_proto_message.tcp_snd_buffer_default = 0
# system_buffer_value_proto_message.tcp_snd_buffer_max = 0

import global_vars
# import system_monitoring_global_vars

remote_ost_index_to_ost_agent_address_dict = Config.parallel_metric_remote_ost_index_to_ost_agent_http_address_dict
ost_rep_backend_socket_name = Config.ost_rep_backend_socket_name
drive_name = Config.parallel_metric_collector_drive_name  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

java_sender_app_path = Config.parallel_metric_java_sender_app_path
java_receiver_app_path = Config.remote_parallel_metric_collector_java_receiver_app_path
# path to read file for transferring
src_path = Config.parallel_metric_collector_src_path
read_lustre_mnt_point_list = Config.parallel_metric_collector_read_lustre_mount_point
# path to save received transferred data
dst_path = Config.remote_parallel_metric_collector_server_saving_directory
write_lustre_mnt_point_list = Config.parallel_metric_collector_write_lustre_mount_point

src_ip = Config.parallel_metric_collector_src_ip
local_port_number = None
dst_ip = Config.parallel_metric_collector_dst_ip
port_number = Config.parallel_metric_collector_port_number

local_ip_range = Config.parallel_metric_collector_local_ip_range
local_port_range = Config.parallel_metric_collector_local_port_range
peer_ip_range = Config.parallel_metric_collector_peer_ip_range
peer_port_range = Config.parallel_metric_collector_peer_port_range

context = None
cloud_server_host = None
cloud_server_port = None

xpub_frontend_public_socket_ip = None
xpub_frontend_public_socket_port = None

# xpub_frontend_socket_ip_receiver = None
# xpub_frontend_socket_port_receiver = None

xsub_backend_socket_name = None

context = zmq.Context()
# receiver_signaling_port = None
if Config.send_to_cloud_mode:
    cloud_server_host = Config.cloud_server_address
    cloud_server_port = Config.cloud_server_port

    xpub_frontend_public_socket_ip = Config.xpub_frontend_socket_ip_sender
    xpub_frontend_public_socket_port = Config.xpub_frontend_socket_port_sender

    xsub_backend_socket_name = Config.xsub_backend_socket_name

    # receiver_signaling_port = Config.receiver_signaling_port

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--label_value', help="label for the dataset", required=True)
parser.add_argument('-rj', '--run_java_app',
                    help="0: run nothing, 1: run client sender app, 2: run server receiver app.",
                    default=0)
parser.add_argument('-jsp', '--java_server_port',
                    help="if running server application it is server listening port, if running client application is java client target connection port",
                    default=port_number)
parser.add_argument('-jlp', '--java_local_port',
                    help="if running client application, is java client connection local port")
parser.add_argument('-jtl', '--java_server_throughput_label',
                    help="if running server application it is label value for java server application to collect throughput",
                    default="0")

args = parser.parse_args()

# global_vars.label_value = args.label_value
global_vars.global_dict["label_value"] = args.label_value
run_java_app = args.run_java_app
if run_java_app == "1":
    port_number = args.java_server_port
    if args.java_local_port:
        local_port_number = args.java_local_port
elif run_java_app == "2":
    java_server_throughput_label = args.java_server_throughput_label


global_vars.should_run.value = True
global_vars.pid.value = 0
# global_vars.sender_process = None
global_vars.global_dict['sender_process'] = None
# global_vars.server_process = None
global_vars.global_dict['server_process'] = None

global_vars.monitor_agent_pid.value = os.getpid()
# global_vars.monitor_agent_process = psutil.Process(int(global_vars.monitor_agent_pid))
# global_vars.global_dict["monitor_agent_process"] = psutil.Process(int(global_vars.monitor_agent_pid.value))
# global_vars.mdt_parent_path = Config.parallel_metric_mdt_parent_path
global_vars.global_dict["mdt_parent_path"] = Config.parallel_metric_mdt_parent_path
global_vars.ready_to_publish.value = False
if not Config.send_to_cloud_mode:
    Path("./sender/logs").mkdir(parents=True, exist_ok=True)
    Path("./sender/overhead_logs").mkdir(parents=True, exist_ok=True)
    Path("./SimpleSenderLog").mkdir(parents=True, exist_ok=True)

    Path("./receiver/logs").mkdir(parents=True, exist_ok=True)
    Path("./receiver/overhead_logs").mkdir(parents=True, exist_ok=True)
    Path("./receiver/SimpleReceiverLog").mkdir(parents=True, exist_ok=True)

publisher_process = None
if Config.send_to_cloud_mode:
    publisher_process = SendToRabbit(xsub_backend_socket_name, context, Config.cluster_name, Config.rabbit_log_queue_name, Config.heartbeat_queue_name, global_vars.ready_to_publish, Config.rabbit_host, Config.rabbit_port, Config.rabbitmq_heartbeat_interval)
    publisher_process.start()

global_metrics_collector_process = globalMetricsMonitor(1, global_vars.system_cpu_mem_usage_dict,
                                                        global_vars.system_buffer_value, global_vars.system_buffer_value_dict,

                                                        Config.lustre_NIC_name, global_vars.system_lustre_nic_io_dict)
global_metrics_collector_process.start()

global_client_ost_metrics_collector_process = LustreClientOstMetricSharedMemCache(global_vars.client_ost_metrics_dict, 1)
global_client_ost_metrics_collector_process.start()

# global_client_mdt_metrics_collector_process = LustreClientMdtMetricSharedMemCache(global_vars.client_mdt_metrics_dict, 1)
# global_client_mdt_metrics_collector_process.start()

transfer_validator = TransferValidationStrategy_2()
transfer_manager = TransferManager(context, xsub_backend_socket_name, ost_rep_backend_socket_name,
                                   Config.client_ost_rep_backend_socket_name,
                                   remote_ost_index_to_ost_agent_address_dict, read_lustre_mnt_point_list,
                                   write_lustre_mnt_point_list,global_vars.global_dict["mdt_parent_path"],
                                   global_vars.global_dict["label_value"], global_vars.ready_to_publish,
                                   global_vars.system_cpu_mem_usage_dict, global_vars.system_buffer_value_dict,
                                   global_vars.client_ost_metrics_dict,
                                   global_vars.system_lustre_nic_io_dict)

discovery_process = TransferDiscovery(local_ip_range, peer_ip_range, local_port_range, peer_port_range, transfer_validator, transfer_manager, discovery_cycle=1)
discovery_process.start()

ost_metric_cache_process = LustreOstMetricCache(context, Config.ost_cache_size, Config.ost_cache_ttl, Config.ost_rep_backend_socket_name, remote_ost_index_to_ost_agent_address_dict)
ost_metric_cache_process.start()

# client_ost_metric_process = LustreClientOstMetricCache(context, Config.client_ost_cache_size, Config.client_ost_cache_ttl, Config.client_ost_rep_backend_socket_name)
# client_ost_metric_process.start()

# client_mdt_metric_process = LustreClientMdtMetricCache(context, Config.client_mdt_cache_size, Config.client_mdt_cache_ttl, Config.client_mdt_rep_backend_socket_name)
# client_mdt_metric_process.start()

if run_java_app == "1":
    # pass
    file_transfer_thread = FileTransferThread(str(0), java_sender_app_path, dst_ip, port_number, src_path,
                                              global_vars.global_dict["label_value"],
                                              src_ip, local_port_number)
    file_transfer_thread.start()
    file_transfer_thread.join()
elif run_java_app == "2":
    # pass
    server_thread = RunServerThread(str(0), java_receiver_app_path, dst_path,
                                    port_number, java_server_throughput_label)
    server_thread.start()
    server_thread.join()

# while True:
#     print(global_vars.ready_to_publish.value)
#     # print(global_vars.system_cpu_mem_usage_dict)
#     # print(system_monitoring_global_vars.system_cpu_mem_usage[0], system_monitoring_global_vars.system_cpu_mem_usage[1])
#     # print(system_monitoring_global_vars.system_cpu_mem_usage_dict)
#     time.sleep(1)

discovery_process.join()
global_client_ost_metrics_collector_process.join()
# global_client_mdt_metrics_collector_process.join()
global_metrics_collector_process.join()
ost_metric_cache_process.join()
# client_ost_metric_process.join()
# client_mdt_metric_process.join()
if publisher_process:
    publisher_process.join()

is_transfer_done = True
