import threading
import time
from pathlib import Path
from subprocess import PIPE, Popen
import subprocess
import sys, traceback
from subprocess import check_output
import psutil

from NetworkStatistics.NetworkStatisticsLogCollector_ss import NetworkStatisticsLogCollectorSS
from AgentMetricCollector.statistics_log_collector import StatisticsLogCollector

# from DiskStatistics.DiskStatisticsLogCollector import DiskStatisticsLogCollector
# from dataset_generator.normal_filesystem.AgentMetricCollector.collectors.system_metric_collector import collect_system_metrics
# from buffer_value_collector import get_buffer_value

src_ip = "127.0.0.1"
dst_ip = "134.197.95.46"
port_number = "50505"
time_length = 3600  # one hour data
drive_name = "sda"  # drive_name = "sda" "nvme0n1" "xvdf" can be checked with lsblk command on ubuntu

# path to read file for transferring
src_path = "/home/esaeedizade/dataDir/srcData/"
# path to save received transferred data
dst_path = "/home/esaeedizade/dataDir/dstData/"
start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file
label_value = int(sys.argv[1])
should_run = True
pid = 0
sender_process = None
is_transfer_done = False


# T ODO check if this is necessary for normal filesystem
# mdt_parent_path = '/proc/fs/lustre/mdc/'

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
    comm_ss = ['java', '../utilities/SimpleSender1.java', dst_ip, port_number, src_path, str(label_value)]
    strings = ""
    proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
    pid = check_output(['pidof', '-s', 'java', 'SimpleSender1.java'])
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
    # disk_statistics_collector = DiskStatisticsLogCollector(drive_name=drive_name, sector_conversion_fctr=2)
    statistics_collector = StatisticsLogCollector(disk_drive_name=drive_name, sector_conversion_fctr=2)

    for x in parts:
        if "lustre" in x:
            isparallel_file_system = True

    if not isparallel_file_system:
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
                    system_value_list = statistics_collector.collect_system_metrics(pid, sender_process)
                    buffer_value_list = statistics_collector.get_buffer_value()

                    output_string = str(time.time()) + ","
                    output_string += network_statistics_collector.get_log_str()
                    output_string += "," + statistics_collector.get_disk_statistics_log_str()
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
