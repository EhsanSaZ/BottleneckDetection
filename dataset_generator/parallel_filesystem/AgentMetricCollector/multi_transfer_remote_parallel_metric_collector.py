
import os
import time
from pathlib import Path
import psutil
import argparse
import zmq
import remote_global_vars
from Config import Config

from run_server_thread import RunServerThread
from helper_threads import fileWriteThread, overheadFileWriteThread, globalMetricsMonitor
from receiver_publisher import SendToCloud
from discovery.transfer_validation_strategy1 import transferValidation_strategy_1
from discovery.transfer_discovery import TransferDiscovery
from remote_transfer_manager import RemoteTransferManager

# try:
#     from discovery.transfer_validation_strategy1 import transferValidation_strategy_1
# except ModuleNotFoundError:
#     from .discovery.transfer_validation_strategy1 import transferValidation_strategy_1

remote_ost_index_to_ost_agent_address_dict = Config.remote_parallel_metric_collector_remote_ost_index_to_ost_agent_address_dict
time_length = Config.remote_parallel_metric_collector_time_length  # one hour data
drive_name = Config.remote_parallel_metric_collector_drive_name  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

# must be from root dir /
java_receiver_app_path = Config.remote_parallel_metric_collector_java_receiver_app_path
server_saving_directory = Config.remote_parallel_metric_collector_server_saving_directory

server_ip = Config.remote_parallel_metric_collector_server_ip
server_port_range = Config.remote_parallel_metric_collector_server_port_range
client_ip = Config.remote_parallel_metric_collector_client_ip
client_port_range = Config.remote_parallel_metric_collector_client_port_range

server_port_number = Config.remote_parallel_metric_collector_server_port_number

start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file

context = None
ready_to_publish = False
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
parser.add_argument('-jsp', '--java_server_port', help="starting port for java server process",
                    default=server_port_number)
parser.add_argument('-jtl', '--java_server_throughput_label', help="starting port for java server process",
                    required=True)

args = parser.parse_args()

label_value = args.label_value
server_port_number = args.java_server_port
java_server_throughput_label = args.java_server_throughput_label

if args.transfer_id:
    transfer_id = args.transfer_id
else:
    transfer_id = "{}_{}".format(Config.parallel_metric_collector_src_ip, Config.parallel_metric_collector_dst_ip)

remote_global_vars.should_run = True
remote_global_vars.pid = 0
remote_global_vars.server_process = None

remote_global_vars.receiver_monitor_agent_pid = os.getpid()
remote_global_vars.receiver_monitor_agent_process = psutil.Process(int(remote_global_vars.receiver_monitor_agent_pid))

remote_global_vars.mdt_parent_path = Config.remote_parallel_metric_collector_mdt_parent_path
remote_global_vars.ready_to_publish = False


#     receiver_publisher.bind("tcp://{}:{}".format(Config.zmq_receiver_publisher_bind_addr, Config.zmq_receiver_publisher_port))
# else:
#     receiver_publisher = None

Path("./receiver/logs").mkdir(parents=True, exist_ok=True)
Path("./receiver/overhead_logs").mkdir(parents=True, exist_ok=True)
Path("./receiver/SimpleReceiverLog").mkdir(parents=True, exist_ok=True)

publisher_thread = None
if Config.send_to_cloud_mode:
    publisher_thread = SendToCloud(xpub_frontend_socket_ip_receiver, xpub_frontend_socket_port_receiver,
                                   xsub_backend_socket_name, context, receiver_signaling_port)
    publisher_thread.start()

# stat_thread = statThread()
# stat_thread.start()
# overhead_write_thread = overheadFileWriteThread("timestamp,processing_time, payload_size, cpu_percent, memory_percent\n")
# overhead_write_thread.start()

global_metrics_collector = globalMetricsMonitor(sleep_time=1)
global_metrics_collector.start()

transfer_validator = transferValidation_strategy_1()
transfer_manager = RemoteTransferManager(context, xsub_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                                         server_saving_directory, remote_global_vars.mdt_parent_path,
                                         remote_global_vars.label_value)
discovery_thread = TransferDiscovery(server_ip, server_port_range, client_ip, client_port_range, transfer_validator,
                                     transfer_manager, discovery_cycle=1)
discovery_thread.start()

# server_thread = RunServerThread(str(0), java_receiver_app_path, server_saving_directory,
#                                 server_port_number, java_server_throughput_label)
# server_thread.start()
# server_thread.join()

# stat_thread.join()
discovery_thread.join()
global_metrics_collector.join()

if publisher_thread:
    publisher_thread.join()

is_transfer_done = True
