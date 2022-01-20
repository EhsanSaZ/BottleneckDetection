import threading
import time
from pathlib import Path
from subprocess import PIPE, Popen
import subprocess
import sys, traceback
from subprocess import check_output
import re
import psutil
import copy

from NetworkStatistics.NetworkStatisticsLogCollector_ss import NetworkStatisticsLogCollectorSS
from system_metric_collector import collect_system_metrics
from buffer_value_collector import get_buffer_value
from file_ost_path_info import collect_file_ost_path_info
from file_mdt_path_info import collect_file_mdt_path_info
from ost_stat_collector import process_ost_stat
from mdt_stat_collector import get_mdt_stat

src_ip = "127.0.0.1"
dst_ip = "192.170.227.252"
port_number = "50505"
time_length = 3600  # one hour data
drive_name = "sda"  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

# path to read file for transferring
src_path = "/home1/08440/tg877399/datadir/srcData/"
# path to save received transferred data
dst_path = "/home1/08440/tg877399/datadir/dstData/"
start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file
label_value = int(sys.argv[1])
should_run = True
pid = 0
sender_process = None
is_transfer_done = False

global mdt_parent_path
mdt_parent_path = '/proc/fs/lustre/mdc/'


class FileTransferThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("\nStarting " + self.name)
        transfer_file(self.name)
        print("\nExiting " + self.name)


def transfer_file(i):
    global pid, label_value, sender_process
    output_file = open("./logs/file_transfer_stat.txt", "a+")
    # T ODO check why use SimpleSender2 for label 29
    # if label_value == 29:
    #     comm_ss = ['java', '../utilities/SimpleSender2.java', dst_ip, port_number, src_path, str(label_value)]
    # else:
    #     comm_ss = ['java', '../utilities/SimpleSender1.java', dst_ip, port_number, src_path, str(label_value)]
    # comm_ss = ['java', '../utilities/SimpleSender1.java', dst_ip, port_number, src_path, str(label_value)]
    comm_ss = ['java', '-cp', '/home1/08440/tg877399/BottleneckDetection/dataset_generator/utilities/', 'SimpleSender1',
               dst_ip, port_number, src_path, str(label_value)]
    strings = ""
    proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
    pid = check_output(['/sbin/pidof', '-s', 'java', 'SimpleSender1.java'])
    print(pid)
    sender_process = psutil.Process(int(pid))
    # global label_value
    output_file.write("label = " + str(label_value) + "\n")
    output_file.write("start time = " + time.ctime() + "\n")
    output_file.flush()
    output_file.close
    while (True):
        line = str(proc.stdout.readline()).replace("\r", "\n")
        strings += line
        # if not line.decode("utf-8"):
        #     break
        strings.replace("\r", "\n")


def collect_stat():
    isparallel_file_system = False
    proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    parts = res.split("\n")
    network_statistics_collector = NetworkStatisticsLogCollectorSS(dst_ip, port_number)
    for x in parts:
        if "lustre" in x:
            isparallel_file_system = True

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
        main_output_string = ""
        ost_stats_so_far = {"req_waittime": 0.0, "req_active": 0.0, "read_bytes": 0.0, "write_bytes": 0.0,
                            "ost_setattr": 0.0, "ost_read": 0.0, "ost_write": 0.0, "ost_get_info": 0.0,
                            "ost_connect": 0.0, "ost_punch": 0.0, "ost_statfs": 0.0, "ost_sync": 0.0,
                            "ost_quotactl": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0}
        while 1:
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
                epoc_time += 1

                if time_diff >= (.1 / sleep_time):
                    system_value_list = collect_system_metrics(pid, sender_process)
                    buffer_value_list = get_buffer_value()
                    ost_path = collect_file_ost_path_info(pid, src_path)
                    mdt_path = collect_file_mdt_path_info(pid, src_path)

                    ost_value_list, ost_stats_so_far = process_ost_stat(ost_path, ost_stats_so_far)

                    mdt_value_list, all_mdt_stat_so_far_dict = get_mdt_stat(mdt_parent_path, mdt_paths,
                                                                            all_mdt_stat_so_far_dict)
                    output_string = network_statistics_collector.get_log_str()

                    global label_value
                    for item in system_value_list:
                        output_string += "," + str(item)
                    for item in buffer_value_list:
                        output_string += "," + str(item)
                    # ost_value_list are metrics with index 79-95 in csv
                    for item in ost_value_list:
                        output_string += "," + str(item)
                    # values with index 96, 97, 98, 99
                    output_string += "," + str(network_statistics_collector.dsack_dups)
                    output_string += "," + str(network_statistics_collector.reord_seen)

                    output_string += "," + str(psutil.cpu_percent())
                    output_string += "," + str(psutil.virtual_memory().percent)

                    # mdt_value_list : total_mdt_numbers at 100
                    # repeat "total_mdt_numbers" of times in list
                    # string of mdt name to use as key for map, foK36 metrics for each mdt
                    for item in mdt_value_list:
                        output_string += "," + str(item)

                    output_string += "," + str(label_value) + "\n"
                    if not is_first_time:
                        main_output_string += output_string
                    else:
                        print("skip first transfer")
                        is_first_time = False

                    epoc_count += 1
                    if epoc_count % 10 == 0:
                        print("transferring file.... ", epoc_count, "label: ", label_value)
                        if epoc_count % 100 == 0:
                            print("transferring file.... ", epoc_count, "label: ", label_value)
                            epoc_count = 0
                        write_thread = fileWriteThread(main_output_string, label_value)
                        write_thread.start()
                        main_output_string = ""
            except:
                traceback.print_exc()
            time.sleep(sleep_time)


class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, label_value):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.label_value = label_value

    def run(self):
        output_file = open("./logs/dataset_" + str(self.label_value) + ".csv", "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


class statThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        collect_stat()


Path("./logs").mkdir(parents=True, exist_ok=True)
Path("./SimpleSenderLog").mkdir(parents=True, exist_ok=True)

stat_thread = statThread()
stat_thread.start()

file_transfer_thread = FileTransferThread(str(0))
file_transfer_thread.start()
file_transfer_thread.join()

is_transfer_done = True
