import argparse
import os
from pathlib import Path
import psutil
import zmq

from Config import Config
from discovery.transfer_discovery import TransferDiscovery
from discovery.transfer_validation_strategy2 import TransferValidationStrategy_2
from transfer_manager import TransferManager
from helper_threads import globalMetricsMonitor
from publisher import SendToCloud
from file_transfer_thread import  FileTransferThread
from run_server_thread import RunServerThread
import global_vars

remote_ost_index_to_ost_agent_address_dict = Config.parallel_metric_remote_ost_index_to_ost_agent_address_dict
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

# receiver_signaling_port = None
if Config.send_to_cloud_mode:
    context = zmq.Context()
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

global_vars.label_value = args.label_value
run_java_app = args.run_java_app
if run_java_app == "1":
    port_number = args.java_server_port
    if args.java_local_port:
        local_port_number = args.java_local_port
elif run_java_app == "2":
    java_server_throughput_label = args.java_server_throughput_label


global_vars.should_run = True
global_vars.pid = 0
global_vars.sender_process = None
global_vars.server_process = None

global_vars.monitor_agent_pid = os.getpid()
global_vars.monitor_agent_process = psutil.Process(int(global_vars.monitor_agent_pid))

global_vars.mdt_parent_path = Config.parallel_metric_mdt_parent_path
global_vars.ready_to_publish = False
if not Config.send_to_cloud_mode:
    Path("./sender/logs").mkdir(parents=True, exist_ok=True)
    Path("./sender/overhead_logs").mkdir(parents=True, exist_ok=True)
    Path("./SimpleSenderLog").mkdir(parents=True, exist_ok=True)

    Path("./receiver/logs").mkdir(parents=True, exist_ok=True)
    Path("./receiver/overhead_logs").mkdir(parents=True, exist_ok=True)
    Path("./receiver/SimpleReceiverLog").mkdir(parents=True, exist_ok=True)

publisher_thread = None
if Config.send_to_cloud_mode:
    publisher_thread = SendToCloud(cloud_server_host, cloud_server_port,
                                   xpub_frontend_public_socket_ip, xpub_frontend_public_socket_port,
                                   xsub_backend_socket_name, context)
    publisher_thread.start()

global_metrics_collector = globalMetricsMonitor(sleep_time=1)
global_metrics_collector.start()

transfer_validator = TransferValidationStrategy_2()
transfer_manager = TransferManager(context, xsub_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                                   read_lustre_mnt_point_list, write_lustre_mnt_point_list, global_vars.mdt_parent_path, global_vars.label_value)
discovery_thread = TransferDiscovery(local_ip_range, peer_ip_range, local_port_range, peer_port_range,
                                     transfer_validator, transfer_manager, discovery_cycle=1)
discovery_thread.start()

if run_java_app == "1":
    # pass
    file_transfer_thread = FileTransferThread(str(0), java_sender_app_path, dst_ip, port_number, src_path,
                                              global_vars.label_value,
                                              src_ip, local_port_number)
    file_transfer_thread.start()
    file_transfer_thread.join()
elif run_java_app == "2":
    # pass
    server_thread = RunServerThread(str(0), java_receiver_app_path, dst_path,
                                    port_number, java_server_throughput_label)
    server_thread.start()
    server_thread.join()

discovery_thread.join()
global_metrics_collector.join()

if publisher_thread:
    publisher_thread.join()

is_transfer_done = True