import argparse
import json
import threading
import time
from pathlib import Path
import socket
from subprocess import PIPE, Popen
import subprocess
import sys, traceback
from subprocess import check_output
import re
import psutil
import copy
import os
import zmq

from NetworkStatistics.NetworkStatisticsLogCollector_ss import NetworkStatisticsLogCollectorSS
from AgentMetricCollector.statistics_log_collector import StatisticsLogCollector
from AgentMetricCollector.Config import Config
from AgentMetricCollector.data_converter import DataConverter
# from remote_ost_stat_collector import process_remote_ost_stats
# from system_metric_collector import collect_system_metrics
# from buffer_value_collector import get_buffer_value
# from file_ost_path_info import collect_file_ost_path_info
# from file_mdt_path_info import collect_file_mdt_path_info
# from ost_stat_collector import process_ost_stat
# from mdt_stat_collector import get_mdt_stat
#from dataset_generator.parallel_filesystem.AgentMetricCollector.ResourceUsageFootprint.get_resource_usage_foot_prints import \
#    ResourceUsageFootprints

src_ip = Config.parallel_metric_collector_src_ip
dst_ip = Config.parallel_metric_collector_dst_ip
port_number = Config.parallel_metric_collector_port_number
remote_ost_index_to_ost_agent_address_dict = Config.parallel_metric_remote_ost_index_to_ost_agent_address_dict
time_length = Config.parallel_metric_collector_time_length  # one hour data
drive_name = Config.parallel_metric_collector_drive_name  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

# path to read file for transferring
src_path = Config.parallel_metric_collector_src_path
# path to save received transferred data
dst_path = Config.parallel_metric_collector_dst_path
start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--label_value', help="label for the dataset", required=True)
parser.add_argument('-i', '--transfer_id', help="transfer id for sending to cloud")
parser.add_argument('-jsp', '--java_server_port', help="starting port for java sender process", default=port_number)

args = parser.parse_args()

label_value = args.label_value
port_number = args.java_server_port

if not args.transfer_id:
    transfer_id = args.transfer_id
else:
    transfer_id = "{}_{}".format(Config.parallel_metric_collector_src_ip, Config.parallel_metric_collector_dst_ip)

should_run = True
pid = 0
sender_process = None
is_transfer_done = False

sender_monitor_agent_pid = os.getpid()
sender_monitor_agent_process = psutil.Process(int(sender_monitor_agent_pid))

global mdt_parent_path
mdt_parent_path = Config.parallel_metric_mdt_parent_path

java_sender_app_path = Config.parallel_metric_java_sender_app_path

context = zmq.Context()
sender_publisher = context.socket(zmq.PUB)
sender_publisher.bind("tcp://{}:{}".format(Config.zmq_sender_publisher_bind_addr, Config.zmq_sender_publisher_port))

class FileTransferThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("\nStarting Java application in a process" + self.name)
        transfer_file(self.name)
        print("\nExiting thread" + self.name)


def transfer_file(i):
    global pid, label_value, sender_process
    output_file = open("./logs/file_transfer_stat.txt", "a+")
    # T ODO check why use SimpleSender2 for label 29
    # if label_value == 29:
    #     comm_ss = ['java', '../utilities/SimpleSender2.java', dst_ip, port_number, src_path, str(label_value)]
    # else:
    #     comm_ss = ['java', '../utilities/SimpleSender1.java', dst_ip, port_number, src_path, str(label_value)]
    comm_ss = ['java', java_sender_app_path, dst_ip, port_number, src_path, str(label_value)]
    # comm_ss = ['java', '-cp', '/home1/08440/tg877399/BottleneckDetection/dataset_generator/utilities/', 'SimpleSender1',
    #            dst_ip, port_number, src_path, str(label_value)]
    strings = ""
    proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
    # pid = check_output(['/sbin/pidof', '-s', 'java', 'SimpleSender1.java'])
    # pid = check_output(['/bin/pidof', '-s', 'java', 'SimpleSender1.java'])
    pid = str(proc.pid)
    print(pid)
    sender_process = psutil.Process(int(pid))
    # global label_value
    output_file.write("label = " + str(label_value) + "\n")
    output_file.write("start time = " + time.ctime() + "\n")
    output_file.flush()
    output_file.close
    # while (True):
    #     line = str(proc.stdout.readline()).replace("\r", "\n")
    #     strings += line
        # if not line.decode("utf-8"):
        #     break
        # strings.replace("\r", "\n")


def collect_stat():
    isparallel_file_system = False
    proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    parts = res.split("\n")
    network_statistics_collector = NetworkStatisticsLogCollectorSS(dst_ip, port_number)
    statistics_collector = StatisticsLogCollector()
    # agent_resource_usage_collector = ResourceUsageFootprints()
    data_converter = DataConverter(file_system="lustre", prefix="sender_")
    for x in parts:
        if "lustre" in x:
            isparallel_file_system = True
    # T ODO REMOVE THIS LINE ITS JUST A TEST
    # isparallel_file_system = True

    if isparallel_file_system:
        mdt_paths = []
        mdt_stat_so_far_general = {"req_waittime": 0.0, "req_active": 0.0, "mds_getattr": 0.0,
                                   "mds_getattr_lock": 0.0, "mds_close": 0.0, "mds_readpage": 0.0,
                                   "mds_connect": 0.0, "mds_get_root": 0.0, "mds_statfs": 0.0,
                                   "mds_sync": 0.0, "mds_quotactl": 0.0, "mds_getxattr": 0.0,
                                   "mds_hsm_state_set": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0,
                                   "seq_query": 0.0, "fld_query": 0.0,
                                   "md_stats": {
                                       "close": 0.0, "create": 0.0, "enqueue": 0.0, "getattr": 0.0, "intent_lock": 0.0,
                                       "link": 0.0, "rename": 0.0, "setattr": 0.0, "fsync": 0.0, "read_page": 0.0,
                                       "unlink": 0.0, "setxattr": 0.0, "getxattr": 0.0,
                                       "intent_getattr_async": 0.0, "revalidate_lock": 0.0
                                   }}
        all_mdt_stat_so_far_dict = {}
        proc = Popen(['ls', '-l', mdt_parent_path], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split("\n")
        for line in res_parts:
            if len(line.strip()) > 0:
                if "total" not in line:
                    parts = line.split(" ")
                    # print(parts)
                    mdt_paths.append(parts[-1])
                    all_mdt_stat_so_far_dict[parts[-1]] = copy.deepcopy(mdt_stat_so_far_general)

        is_controller_port = True
        total_string = ""
        start = time.time()
        initial_time = time.time()
        is_first_time = True
        time_diff = 0
        epoc_time = 0
        sleep_time = 1
        epoc_count = 0
        overhead_epoc_count = 0
        main_output_string = ""
        overhead_main_output_string = ""
        ost_stats_so_far = {"req_waittime": 0.0, "req_active": 0.0, "read_bytes": 0.0, "write_bytes": 0.0,
                            "ost_setattr": 0.0, "ost_read": 0.0, "ost_write": 0.0, "ost_get_info": 0.0,
                            "ost_connect": 0.0, "ost_punch": 0.0, "ost_statfs": 0.0, "ost_sync": 0.0,
                            "ost_quotactl": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0}

        all_remote_ost_stats_so_far = {}
        data_transfer_overhead = 0
        while 1:
            processing_start_time = time.time()
            ### NETWORK METRICS ###
            global is_transfer_done

            if is_transfer_done:
                break
            # If the pid is 0, then the transfer thread is not started yet or the global pid is not updated yet
            # So it is not possible to collect for system metrics, then just skip this iteration
            if sender_process is None:  # or pid == 0
                continue
            try:
                if (is_first_time):
                    initial_time = time.time()
                    # is_first_time = False
                time_diff += 1
                #epoc_time += 1
                if time_diff >= (.1 / sleep_time):
                    # system_value_list = collect_system_metrics(pid, sender_process)
                    system_value_list = statistics_collector.collect_system_metrics(pid, sender_process)
                    buffer_value_list = statistics_collector.get_buffer_value()
                    # ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = collect_file_ost_path_info(pid, src_path)
                    file_ost_path_info = statistics_collector.collect_file_ost_path_info(pid, src_path)
                    if file_ost_path_info is None:
                        continue
                    else:
                        ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = file_ost_path_info
                    # print(ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number)
                    file_mdt_path_info = statistics_collector.collect_file_mdt_path_info(pid, src_path)
                    if file_mdt_path_info is None:
                        continue
                    else:
                        mdt_kernel_path, mdt_dir_name = file_mdt_path_info
                    # print(mdt_kernel_path, mdt_dir_name)
                    ost_value_list, ost_stats_so_far = statistics_collector.process_ost_stat(ost_kernel_path,
                                                                                             ost_dir_name,
                                                                                             ost_stats_so_far)
                    # print (ost_value_list, ost_stats_so_far)
                    # # mdt_value_list, all_mdt_stat_so_far_dict = get_mdt_stat(mdt_parent_path, mdt_paths,
                    # #                                                         all_mdt_stat_so_far_dict)
                    mdt_value_list, mdt_stat_so_far_general = statistics_collector.get_mdt_stat(mdt_parent_path,
                                                                                                mdt_dir_name,
                                                                                                mdt_stat_so_far_general)
                    # print (mdt_value_list, mdt_stat_so_far_general)
                    ost_agent_address = remote_ost_index_to_ost_agent_address_dict.get(ost_number) or ""
                    remote_ost_value_list = [0.0, 0.0]
                    if ost_agent_address != "":
                        remote_ost_stats_so_far = all_remote_ost_stats_so_far.get(remote_ost_dir_name) or {}
                        remote_ost_value_list, remote_ost_stats_so_far = statistics_collector.process_lustre_ost_stats(
                            ost_agent_address, remote_ost_dir_name, remote_ost_stats_so_far)
                        all_remote_ost_stats_so_far[remote_ost_dir_name] = remote_ost_stats_so_far
                    # print (all_remote_ost_stats_so_far)

                    output_string = str(time.time()) + ","
                    output_string += network_statistics_collector.get_log_str()

                    global label_value
                    for item in system_value_list:
                        output_string += "," + str(item)
                    for item in buffer_value_list:
                        output_string += "," + str(item)
                    # ost_value_list are metrics with index 79-95 in csv
                    for item in ost_value_list:
                        output_string += "," + str(item)
                    # values with index 112-147
                    for item in mdt_value_list:
                        output_string += "," + str(item)

                    output_string += "," + str(network_statistics_collector.dsack_dups)
                    output_string += "," + str(network_statistics_collector.reord_seen)

                    output_string += "," + str(psutil.cpu_percent())
                    output_string += "," + str(psutil.virtual_memory().percent)

                    for item in remote_ost_value_list:
                        output_string += "," + str(item)

                    # mdt_value_list : total_mdt_numbers at 100
                    # repeat "total_mdt_numbers" of times in list
                    # string of mdt name to use as key for map, foK36 metrics for each mdt
                    # for item in mdt_value_list:
                    #     output_string += "," + str(item)

                    output_string += "," + str(label_value) + "\n"
                    epoc_count += 1
                    if Config.send_to_cloud_mode and not is_first_time:
                        epoc_time += 1
                        data = {}
                        metrics_data = data_converter.data_str_to_json(output_string)
                        data["transfer_ID"] = transfer_id
                        data["data"] = metrics_data
                        data["sequence_number"] = epoc_time
                        data["is_sender"] = 1
                        body = json.dumps(data)
                        data_transfer_overhead = len(body.encode('utf-8'))
                        # send data to server in a different thread
                        send_thread = sendToCloud(body)
                        send_thread.start()
                    elif not is_first_time:
                        main_output_string += output_string
                        if epoc_count % 10 == 0:
                            print("transferring file.... ", epoc_count, "label: ", label_value)
                            if epoc_count % 100 == 0:
                                print("transferring file.... ", epoc_count, "label: ", label_value)
                                epoc_count = 0
                            write_thread = fileWriteThread(main_output_string, label_value)
                            write_thread.start()
                            main_output_string = ""
                    else:
                        print("skip first transfer")
                        is_first_time = False
            except:
                traceback.print_exc()
            processing_finish_time = time.time()
            processing_time = processing_finish_time - processing_start_time
            # cpu_memory_overhead = agent_resource_usage_collector.get_process_io_stats(sender_monitor_agent_pid,
            #                                                                           sender_monitor_agent_process)
            overhead_output_string = "{},{},{},{},{}\n".format(processing_finish_time,
                                                               processing_time,
                                                               data_transfer_overhead,
                                                               sender_monitor_agent_process.cpu_percent(),
                                                               sender_monitor_agent_process.memory_percent())
            overhead_epoc_count += 1
            if not is_first_time:
                overhead_main_output_string += overhead_output_string
                if overhead_epoc_count % 10 == 0:
                    overhead_epoc_count = 0
                    overhead_write = overheadFileWriteThread(overhead_main_output_string)
                    overhead_write.start()
                    overhead_main_output_string = ""
            time.sleep(sleep_time)


class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, label_value):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.label_value = label_value

    def run(self):
        output_file = open("./sender/logs/dataset_" + str(self.label_value) + ".csv", "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


class overheadFileWriteThread(threading.Thread):
    def __init__(self, overhead_string):
        threading.Thread.__init__(self)
        self.overhead_string = overhead_string

    def run(self):
        output_file = open("./sender/overhead_logs/overhead_footprints.csv", "a+")
        output_file.write(str(self.overhead_string))
        output_file.flush()
        output_file.close()


class sendToCloud(threading.Thread):
    def __init__(self, json):
        threading.Thread.__init__(self)
        self.json = json

    def run(self):
        # T ODO send over the channel to cloud
        sender_publisher.send_json(self.json)
        #print(self.json_str)


class statThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        collect_stat()


Path("./sender/logs").mkdir(parents=True, exist_ok=True)
Path("./sender/overhead_logs").mkdir(parents=True, exist_ok=True)
Path("./SimpleSenderLog").mkdir(parents=True, exist_ok=True)

stat_thread = statThread()
stat_thread.start()
# overhead_write_thread = overheadFileWriteThread("timestamp,processing_time, payload_size, cpu_percent, memory_percent\n")
# overhead_write_thread.start()

file_transfer_thread = FileTransferThread(str(0))
file_transfer_thread.start()
file_transfer_thread.join()

is_transfer_done = True
