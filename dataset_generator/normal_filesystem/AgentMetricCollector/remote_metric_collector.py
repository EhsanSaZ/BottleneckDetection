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

from RemoteNetworkStatistics.RemoteNetworkStatisticsLogCollector_ss import RemoteNetworkStatisticsLogCollectorSS
from statistics_log_collector import StatisticsLogCollector

# from remote_ost_stat_collector import process_remote_ost_stats
# from buffer_value_collector import get_buffer_value
# from file_ost_path_info import collect_file_ost_path_info
# from file_mdt_path_info import collect_file_mdt_path_info
# from ost_stat_collector import process_ost_stat
# from mdt_stat_collector import get_mdt_stat

server_ip = "134.197.95.46"
server_port_number = "50505"
client_ip = "134.197.94.169"


time_length = 3600  # one hour data
drive_name = "sda"  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

# path to save received transferred data
server_saving_directory = "/home/a/receiverDataDir/dstData/"
start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file
label_value = int(sys.argv[1])
should_run = True
pid = 0
server_process = None
is_transfer_done = False

# must be from root dir /
java_receiver_app_path = '/home/a/AgentMetricCollector/collectors/SimpleReceiver1.java'


class RunServerThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("\nStarting " + self.name)
        run_server(self.name)
        print("\nExiting " + self.name)


def run_server(i):
    global pid, label_value, server_process

    comm_ss = ['java', java_receiver_app_path, server_saving_directory]
    proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)

    # pid = check_output(['/sbin/pidof', '-s', 'java', 'SimpleReceiver1.java'])
    # pid = check_output(['/bin/pidof', '-s', 'java', 'SimpleReceiver1.java'])
    pid = str(proc.pid)
    print(pid)
    server_process = psutil.Process(int(pid))
    # global label_value
    # strings = ""
    # while (True):
    #     line = str(sender_process.stdout.readline()).replace("\r", "\n")
    #     strings += line
    #     # if not line.decode("utf-8"):
    #     #     break
    #     strings.replace("\r", "\n")


def collect_stat():
    is_parallel_file_system = False
    proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    parts = res.split("\n")
    for x in parts:
        if "lustre" in x:
            is_parallel_file_system = True

    network_statistics_collector = RemoteNetworkStatisticsLogCollectorSS(server_ip, server_port_number, client_ip)
    remote_statistics_collector = StatisticsLogCollector(disk_drive_name=drive_name, sector_conversion_fctr=2)
    # T ODO REMOVE THIS LINE ITS JUST A TEST
    # is_parallel_file_system = True

    if not is_parallel_file_system:

        is_first_time = True
        time_diff = 0
        epoc_time = 0
        sleep_time = 1
        epoc_count = 0
        main_output_string = ""
        while 1:
            ### NETWORK METRICS ###
            global is_transfer_done

            if is_transfer_done:
                break
            # If the pid is 0, then the transfer thread is not started yet or the global pid is not updated yet
            # So it is not possible to collect for system metrics, then just skip this iteration

            if server_process is None or \
                    pid == 0 or \
                    not network_statistics_collector.check_established_connection_exist():  # or pid == 0
                continue
            try:
                print("COLLECT")
                if is_first_time:
                    initial_time = time.time()
                time_diff += 1
                epoc_time += 1

                if time_diff >= (.1 / sleep_time):
                    system_value_list = remote_statistics_collector.collect_system_metrics(pid, server_process)
                    buffer_value_list = remote_statistics_collector.get_buffer_value()

                    output_string = str(time.time()) + ","
                    output_string += network_statistics_collector.get_log_str()
                    output_string += "," + remote_statistics_collector.get_disk_statistics_log_str()

                    global label_value
                    for item in system_value_list:
                        output_string += "," + str(item)
                    for item in buffer_value_list:
                        output_string += "," + str(item)

                    output_string += "," + str(network_statistics_collector.dsack_dups)
                    output_string += "," + str(network_statistics_collector.reord_seen)

                    output_string += "," + str(psutil.cpu_percent())
                    output_string += "," + str(psutil.virtual_memory().percent)

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
        output_file = open("./receiver/logs/dataset_" + str(self.label_value) + ".csv", "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


class statThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        collect_stat()


Path("./receiver/logs").mkdir(parents=True, exist_ok=True)
Path("./receiver/SimpleReceiverLog").mkdir(parents=True, exist_ok=True)

stat_thread = statThread()
stat_thread.start()

server_thread = RunServerThread(str(0))
server_thread.start()
# server_thread.join()
stat_thread.join()
is_transfer_done = True
