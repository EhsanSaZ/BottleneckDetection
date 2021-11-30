import threading
import time
from subprocess import PIPE, Popen
import subprocess
import sys, traceback
from subprocess import check_output

from dataset_generator import ncollect_system_metrics
from dataset_generator import get_buffer_value

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
    #total 0
    #lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 0 -> /dev/pts/98
    #lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 1 -> /dev/pts/98
    #lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 2 -> /dev/pts/98
    #lr-x------ 1 ehsansa sub102 64 Nov 22 14:09 3 -> /home/ehsansa/sample_text.txt
    res = proc.communicate()[0]
    # print(res)
    res_parts = res.split("\n")
    for line in res_parts:
        if len(line.strip()) > 0:
            if src_path in line:
                slash_index = line.rfind(">")
                file_name = line[slash_index + 1:].strip()

                first_slash_index = file_name.find("/")
                second_slash_index = file_name.find("/", first_slash_index)
                file_mount_point = file_name[first_slash_index+1: first_slash_index + second_slash_index]

                proc = Popen(['lfs', 'getstripe', file_name], universal_newlines=True, stdout=PIPE)
                #/expanse/lustre/scratch/ehsansa/temp_project/sample_text.txt
                #lmm_stripe_count:  1
                #lmm_stripe_size:   1048576
                #lmm_pattern:       raid0
                #lmm_layout_gen:    0
                #lmm_stripe_offset: 61
                #	obdidx		 objid		 objid		 group
                #	    61	      10861858	     0xa5bd22	   0xac0000400
                #
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
                        # Convert obdidx or l_ost_idx from 10 base into hex
                        hex_ost_number = hex(int(ost_number))
                        x_insex = hex_ost_number.rfind("x")
                        hex_ost_number = hex_ost_number[x_insex+1:]
                        proc = Popen(['ls', '-l', '/proc/fs/lustre/osc'], universal_newlines=True, stdout=PIPE)
                        #dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0045-osc-ffff92b94ed33000
                        #dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b900cb0000
                        #dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b94ed33000
                        #dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b900cb0000
                        #dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b94ed33000
                        res = proc.communicate()[0]
                        parts = res.split("\n")
                        ost_str = "-OST" + '{0:04d}'.format(hex_ost_number)
                        for x in range(1, len(parts)):
                            ost_name_parts = parts[x].split(" ")
                            for part in ost_name_parts:
                                if file_mount_point in part and ost_str in part and "OST" in part:
                                    first_dash_index = part.find("-")
                                    second_dash_index = part.find("-", first_dash_index + 1)

                                    first_part = part[:first_dash_index]
                                    second_part = part[second_dash_index+1:]

                                    # ost_str = "-OST" + '{0:04d}'.format(hex_ost_number)

                                    ost_path = '/proc/fs/lustre/osc/' + first_part + ost_str + second_part

                                    # print(ost_path)
                                    return ost_path
                            break


# TODO check this function work correctly
def process_ost_stat(ost_path):
    value_list = []
    proc = Popen(['cat', ost_path + "/stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    #snapshot_time             1637627183.394337 secs.usecs
    #req_waittime              393905757 samples [usec] 31 17820911 483362372205 28824671200467887
    #req_active                393906200 samples [reqs] 1 8243 1164349055 731470318467
    #read_bytes                299768458 samples [bytes] 0 4194304 6895163247966 -3193831078871982772
    #write_bytes               10208130 samples [bytes] 1 4194304 10917616761706 4366299781827334380
    #ost_setattr               8288718 samples [usec] 37 6862915 2072463399 268309705137179
    #ost_read                  299768458 samples [usec] 60 17820911 271513537128 5512071507059074
    #ost_write                 10208130 samples [usec] 86 15329179 98396534435 5245570501603571
    #ost_get_info              5086 samples [usec] 94 234665 2150496 74601868096
    #ost_connect               2 samples [usec] 39418 394674 434092 157321345000
    #ost_punch                 2025537 samples [usec] 44 4425929 658817331 125468513749227
    #ost_statfs                4583100 samples [usec] 34 2354832 1137583809 27790060662971
    #ost_sync                  85484 samples [usec] 35 2683564 407420351 20564344321901
    #ost_quotactl              1070893 samples [usec] 38 1131469 294654538 2901933400418
    #ldlm_cancel               31083060 samples [usec] 31 12008431 99565826195 17460575057288663
    #obd_ping                  43765 samples [usec] 52 130743 28356809 55768300189
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


def collect_stat():
    isparallel_file_system = False
    proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    parts = res.split("\n")

    for x in parts:
        if "lustre" in x:
            isparallel_file_system = True

    if isparallel_file_system:
        # TODO check this works correctly
        mdt_paths = []
        proc = Popen(['ls', '-l', mdt_parent_path], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split("\n")
        for line in res_parts:
            if len(line.strip()) > 0:
                if "total" not in line:
                    parts = line.split(" ")
                    # print(parts)
                    mdt_paths.append(parts[-1])
        is_controller_port = True
        total_string = ""
        start = time.time()
        initial_time = time.time()
        total_rtt_value = 0
        total_pacing_rate = 0
        is_first_time = True
        avg_wait_time = 0
        total_wait_time = 0
        total_cwnd_value = 0
        total_rto_value = 0
        byte_ack = 0
        byte_ack_so_far = 0
        data_segs_out = 0
        segs_out = 0
        data_seg_out_so_far = 0
        seg_out_so_far = 0
        segs_in = 0
        seg_in_so_far = 0
        retrans = 0
        total_ssthresh_value = 0
        total_ost_read = 0
        send = 0
        unacked = 0
        rcv_space = 0
        time_diff = 0
        epoc_time = 0
        has_transfer_started = False
        sleep_time = .1
        epoc_count = 0
        main_output_string = ""
        total_mss_value = 0
        send_buffer_value = 0

        while 1:
            ### NETWORK METRICS ###
            global is_transfer_done

            if is_transfer_done:
                break
            try:
                comm_ss = ['ss', '-tanp', '-i', 'state', 'ESTABLISHED', 'dst', dst_ip]
                ss_proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
                line_in_ss = str(ss_proc.stdout.read())
                if line_in_ss.count(dst_ip) >= 1:
                    if (is_first_time):
                        initial_time = time.time()
                        is_first_time = False

                    parts = line_in_ss.split("\\n")

                    # for part in parts:
                    #     print(part)

                    time_diff += 1
                    epoc_time += 1

                    for x in range(len(parts)):
                        if dst_ip in parts[x] and port_number in parts[x]:
                            first_parts = parts[x].split(" ")
                            first_list = []
                            for item in first_parts:
                                if len(item.strip()) > 0:
                                    first_list.append(item)

                            send_buffer_value = int(first_list[1].strip())
                            sender_part = first_list[-1].strip()
                            user_parts = sender_part.split(",")
                            process_id_part = user_parts[1].strip()
                            equal_index = process_id_part.find("=")
                            # TODO check this process_id with global pid
                            process_id = int(process_id_part[equal_index + 1:])

                            if (is_first_time):
                                initial_time = time.time()
                                is_first_time = False

                            metrics_line = parts[x + 1].strip("\\t").strip()
                            metrics_parts = metrics_line.split(" ")

                            for y in range(len(metrics_parts)):
                                if "data_segs_out" in metrics_parts[y]:
                                    pass
                                elif "rto" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    total_rto_value = value

                                elif "rtt" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    e_index = metrics_parts[y].find("/")
                                    value = float(metrics_parts[y][s_index + 1:e_index])
                                    total_rtt_value = value

                                elif "mss" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    # print("value ",value)
                                    total_mss_value = value

                                elif "cwnd" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    total_cwnd_value = value

                                elif "ssthresh" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    total_ssthresh_value = value

                                elif "bytes_acked" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    byte_ack = (value - byte_ack_so_far)
                                    byte_ack_so_far = value

                                elif "segs_out" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    # print("value ", value)
                                    # print("seg_out_so_far ", seg_out_so_far)
                                    segs_out = (value - seg_out_so_far)
                                    seg_out_so_far = value

                                elif "segs_in" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    segs_in = (value - seg_in_so_far)
                                    seg_in_so_far = value

                                elif "send" in metrics_parts[y]:
                                    value = metrics_parts[y + 1].strip()
                                    send = value

                                elif "pacing_rate" in metrics_parts[y]:
                                    value = metrics_parts[y + 1].strip()
                                    total_pacing_rate = value

                                elif "unacked" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    unacked = value

                                elif "retrans" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    e_index = metrics_parts[y].find("/")
                                    value = float(metrics_parts[y][s_index + 1:e_index])
                                    retrans = value

                                elif "rcv_space" in metrics_parts[y]:
                                    s_index = metrics_parts[y].find(":")
                                    value = float(metrics_parts[y][s_index + 1:])
                                    rcv_space = value
                                # TODO COMPLETE THIS PART!
                    if time_diff >= (.1 / sleep_time):
                        avg_rto_value = total_rto_value
                        avg_rtt_value = total_rtt_value
                        avg_mss_value = total_mss_value
                        avg_cwnd_value = total_cwnd_value
                        avg_ssthresh_value = total_ssthresh_value
                        avg_byte_ack = byte_ack / (1024 * 1024)
                        avg_seg_out = segs_out
                        avg_seg_in = segs_in
                        avg_send_value = send
                        p_avg_value = total_pacing_rate
                        avg_unacked_value = unacked
                        avg_retrans = retrans
                        avg_rcv_space = rcv_space

                    system_value_list = collect_system_metrics(process_id)
                    buffer_value_list = get_buffer_value()
                    # TODO check these functions to work correctly
                    ost_path = collect_file_path_info(process_id)
                    ost_value_list = process_ost_stat(ost_path)
                    mdt_value_list = get_mdt_stat(mdt_paths)

                    output_string = str(avg_rtt_value) + "," + str(p_avg_value) + "," + str(avg_cwnd_value) + "," + \
                                    str(avg_rto_value) + "," + str(avg_byte_ack) + "," + str(avg_seg_out) + "," + \
                                    str(retrans) + "," + str(avg_mss_value) + "," + str(avg_ssthresh_value) + "," + \
                                    str(avg_seg_in) + "," + str(avg_send_value) + "," + str(avg_unacked_value) + "," + \
                                    str(avg_rcv_space) + "," + str(send_buffer_value)

                    for item in system_value_list:
                        output_string += "," + str(item)
                    for item in buffer_value_list:
                        output_string += "," + str(item)
                    for item in ost_value_list:
                        output_string += "," + str(item)
                    for item in mdt_value_list:
                        output_string += "," + str(item)

                    output_string += "," + str(label_value) + "\n"
                    main_output_string += output_string

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
        output_file = open("./logs/dataset_"+str(self.label_value)+".csv","a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()

class statThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        collect_stat()
