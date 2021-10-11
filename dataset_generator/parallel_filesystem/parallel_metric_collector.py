import threading
import time
from subprocess import PIPE, Popen
import subprocess
import sys, traceback
from subprocess import check_output

from dataset_generator.utilities.system_metric_collector import collect_system_metrics
from dataset_generator.utilities.butter_value_collector import get_buffer_value
from dataset_generator.utilities.disk_stat_collector import get_disk_stat

src_ip = "127.0.0.1"
dst_ip = "127.0.0.1"
port_number = "50505"
time_length = 3600  # one hour data
drive_name = "sda"

# path to read file for transferring
src_path = "/home/esaeedizade/Desktop/srcData/"
# path to save received transferred data
dst_path = "/home/esaeedizade/Desktop/dstData/"
start_time_global = time.time()
# label_value normal = 0, more labeled can be checked from command bash file
label_value = int(sys.argv[1])
should_run = True
pid = 0
is_transfer_done = False

# TODO check this path with the path in target environment
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
    global pid, label_value
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


# TODO check this function work correctly
def collect_file_path_info(pid):
    proc = Popen(['ls', '-l', '/proc/' + str(pid).strip() + '/fd/'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    # print(res)
    res_parts = res.split("\n")
    for line in res_parts:
        if len(line.strip()) > 0:
            if src_path in line:
                slash_index = line.rfind(">")
                file_name = line[slash_index + 1:].strip()
                proc = Popen(['lfs', 'getstripe', file_name], universal_newlines=True, stdout=PIPE)
                res1 = proc.communicate()[0]
                res_parts1 = res1.split("\n")
                for x in range(len(res_parts1)):
                    if "obdidx" in res_parts1[x] or "l_ost_idx" in res_parts1[x]:
                        ost_number = 0
                        if "obdidx" in res_parts1[x]:
                            parts = res_parts1[x + 1].strip().split("\t")
                            # print(parts)
                            # print(parts[0])
                            ost_number = int(parts[0].strip())
                        else:
                            parts = res_parts1[x].strip().split("l_ost_idx: ")[1].split(",")
                            ost_number = int(parts[0].strip())
                        proc = Popen(['ls', '-l', '/proc/fs/lustre/osc'], universal_newlines=True, stdout=PIPE)
                        res = proc.communicate()[0]
                        parts = res.split("\n")
                        for x in range(1, len(parts)):
                            ost_name_parts = parts[x].split(" ")
                            for part in ost_name_parts:
                                if "OST" in part:
                                    first_dash_index = part.find("-")
                                    sencond_dash_index = part.find("-", first_dash_index)

                                    firstpart = part[:first_dash_index]
                                    secondpart = part[first_dash_index + sencond_dash_index:]

                                    ost_str = "-OST" + '{0:04d}'.format(ost_number)

                                    ost_path = '/proc/fs/lustre/osc/' + firstpart + ost_str + secondpart

                                    # print(ost_path)
                                    return ost_path
                            break


# TODO check this function work correctly
def process_ost_stat(ost_path):
    value_list = []
    proc = Popen(['cat', ost_path + "/stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    for metric_line in res_parts:
        if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
            tokens = str(metric_line).split(" ")
            value_list.append(tokens[0])
            value = float(tokens[len(tokens) - 2])
            value_list.append(value)

    proc = Popen(['cat', ost_path + "/rpc_stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    for metric_line in res_parts:
        if "pending read pages" in metric_line:
            index = metric_line.find(":")
            value = float(metric_line[index + 1:])
            value_list.append(value)

        if "read RPCs in flight" in metric_line:
            index = metric_line.find(":")
            value = float(metric_line[index + 1:])
            value_list.append(value)
    return value_list


# TODO check this function work correctly
def process_mds_rpc(mdt_path):
    proc = Popen(['cat', mdt_path + "/import"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    value_list = []
    for metric_line in res_parts:
        if "avg_waittime:" in metric_line:
            s_index = metric_line.find(":")
            e_index = metric_line.find("usec")
            avg_waittime = float(metric_line[s_index + 1:e_index].strip())
            value_list.append(avg_waittime)

        if "inflight:" in metric_line:
            s_index = metric_line.find(":")
            inflight = float(metric_line[s_index + 1:].strip())
            value_list.append(inflight)

        if "unregistering:" in metric_line:
            s_index = metric_line.find(":")
            unregistering = float(metric_line[s_index + 1:].strip())
            value_list.append(unregistering)

        if "timeouts:" in metric_line:
            s_index = metric_line.find(":")
            timeouts = float(metric_line[s_index + 1:].strip())
            value_list.append(timeouts)

    return value_list


# TODO check this function work correctly
def process_mdt_stat(mdt_path):
    value_list = []
    proc = Popen(['cat', mdt_path + "/stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    for metric_line in res_parts:
        if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
            tokens = str(metric_line).split(" ")
            value_list.append(tokens[0])
            value = float(tokens[len(tokens) - 2])
            value_list.append(value)

    proc = Popen(['cat', mdt_path + "/md_stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    for metric_line in res_parts:
        if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
            tokens = str(metric_line).split(" ")
            value_list.append(tokens[0])
            value = float(tokens[len(tokens) - 3])
            value_list.append(value)
    return value_list


# TODO check this function work correctly
def get_mdt_stat(mdt_paths):
    global mdt_parent_path
    value_list = []
    for path in mdt_paths:
        value_list += process_mds_rpc(mdt_parent_path + path)
        value_list += process_mdt_stat(mdt_parent_path + path)
    return value_list

