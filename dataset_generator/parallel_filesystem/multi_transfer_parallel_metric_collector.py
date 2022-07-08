import argparse
import os
from pathlib import Path

import psutil
import zmq

from AgentMetricCollector.Config import Config
from AgentMetricCollector.discovery.transfer_discovery import TransferDiscovery
from AgentMetricCollector.discovery.transfer_validation_strategy1 import transferValidation_strategy_1
from AgentMetricCollector import system_monitoring_global_vars
from transfer_manager import transferManager
from file_transfer_thread import FileTransferThread
from dataset_generator.parallel_filesystem.AgentMetricCollector.helper_threads import globalMetricsMonitor
from sender_publisher import sendToCloud
import global_vars

remote_ost_index_to_ost_agent_address_dict = Config.parallel_metric_remote_ost_index_to_ost_agent_address_dict
time_length = Config.parallel_metric_collector_time_length  # one hour data
drive_name = Config.parallel_metric_collector_drive_name  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

java_sender_app_path = Config.parallel_metric_java_sender_app_path
# path to read file for transferring
src_path = Config.parallel_metric_collector_src_path
# path to save received transferred data
dst_path = Config.parallel_metric_collector_dst_path

src_ip = Config.parallel_metric_collector_src_ip
src_port_range = Config.parallel_metric_collector_src_port_range
dst_ip = Config.parallel_metric_collector_dst_ip
dst_port_range = Config.parallel_metric_collector_dst_port_range

port_number = Config.parallel_metric_collector_port_number
local_port_number = None

context = None
cloud_server_host = None
cloud_server_port = None

xpub_frontend_socket_ip_sender = None
xpub_frontend_socket_port_sender = None

xpub_frontend_socket_ip_receiver = None
xpub_frontend_socket_port_receiver = None

xsub_backend_socket_name = None

receiver_signaling_port = None
if Config.send_to_cloud_mode:
    context = zmq.Context()
    cloud_server_host = Config.cloud_server_address
    cloud_server_port = Config.cloud_server_port

    xpub_frontend_socket_ip_sender = Config.xpub_frontend_socket_ip_sender
    xpub_frontend_socket_port_sender = Config.xpub_frontend_socket_port_sender

    xpub_frontend_socket_ip_receiver = Config.xpub_frontend_socket_ip_receiver
    xpub_frontend_socket_port_receiver = Config.xpub_frontend_socket_port_receiver

    xsub_backend_socket_name = Config.xsub_backend_socket_name

    receiver_signaling_port = Config.receiver_signaling_port

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--label_value', help="label for the dataset", required=True)
parser.add_argument('-i', '--transfer_id', help="transfer id for sending to cloud")
parser.add_argument('-jsp', '--java_server_port', help="server listening port", default=port_number)
parser.add_argument('-jlp', '--java_local_port', help="client connection port")

args = parser.parse_args()

global_vars.label_value = args.label_value
port_number = args.java_server_port

if args.transfer_id:
    transfer_id = args.transfer_id
else:
    transfer_id = "{}_{}".format(Config.parallel_metric_collector_src_ip, Config.parallel_metric_collector_dst_ip)

if args.java_local_port:
    local_port_number = args.java_local_port

global_vars.should_run = True
global_vars.pid = 0
global_vars.sender_process = None
global_vars.sender_monitor_agent_pid = os.getpid()
global_vars.sender_monitor_agent_process = psutil.Process(int(global_vars.sender_monitor_agent_pid))

system_monitoring_global_vars.system_cpu_usage = -1
system_monitoring_global_vars.system_memory_usage = -1
system_monitoring_global_vars.system_buffer_value = []
global_vars.mdt_parent_path = Config.parallel_metric_mdt_parent_path
global_vars.ready_to_publish = False

Path("./sender/logs").mkdir(parents=True, exist_ok=True)
Path("./sender/overhead_logs").mkdir(parents=True, exist_ok=True)
Path("./SimpleSenderLog").mkdir(parents=True, exist_ok=True)

publisher_thread = None
if Config.send_to_cloud_mode:
    publisher_thread = sendToCloud(cloud_server_host, cloud_server_port,
                                   xpub_frontend_socket_ip_sender, xpub_frontend_socket_port_sender,
                                   xpub_frontend_socket_ip_receiver, xpub_frontend_socket_port_receiver,
                                   xsub_backend_socket_name, context, receiver_signaling_port)
    publisher_thread.start()

# overhead_write_thread = overheadFileWriteThread("timestamp,processing_time, payload_size, cpu_percent, memory_percent\n")
# overhead_write_thread.start()

global_metrics_collector = globalMetricsMonitor(sleep_time=1)
global_metrics_collector.start()

transfer_validator = transferValidation_strategy_1()
transfer_manager = transferManager(context, xsub_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                                   src_path, global_vars.mdt_parent_path, global_vars.label_value)
discovery_thread = TransferDiscovery(src_ip, src_port_range, dst_ip, dst_port_range, transfer_validator,
                                     transfer_manager, discovery_cycle=1)
discovery_thread.start()

# file_transfer_thread = FileTransferThread(str(0), java_sender_app_path, dst_ip, port_number, src_path,
#                                           global_vars.label_value,
#                                           src_ip, local_port_number)
# file_transfer_thread.start()
# file_transfer_thread.join()
discovery_thread.join()
global_metrics_collector.join()

if publisher_thread:
    publisher_thread.join()

is_transfer_done = True
