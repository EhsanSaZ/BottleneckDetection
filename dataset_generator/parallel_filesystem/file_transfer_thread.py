import subprocess
import threading

import psutil
import global_vars


class FileTransferThread(threading.Thread):
    def __init__(self, name, java_sender_app_path, dst_ip, port_number, src_path, label_value, src_ip=None,
                 local_port_number=None):
        threading.Thread.__init__(self)
        self.name = name
        self.java_sender_app_path = java_sender_app_path
        self.dst_ip = dst_ip
        self.port_number = port_number
        self.src_path = src_path
        self.label_value = label_value
        self.src_ip = src_ip
        self.local_port_number = local_port_number

    def run(self):
        print("\nStarting Java application in a process" + self.name)
        self.transfer_file(self.name)
        print("\nExiting thread file transfer thread" + self.name)

    def transfer_file(self, i):
        # global pid, label_value, sender_process
        # print(global_vars.pid, global_vars.label_value, global_vars.sender_process)
        if self.local_port_number:
            comm_ss = ['java', self.java_sender_app_path, self.dst_ip, self.port_number, self.src_path,
                       self.label_value, self.src_ip, self.local_port_number]
        else:
            comm_ss = ['java', self.java_sender_app_path, self.dst_ip, self.port_number, self.src_path,
                       self.label_value]
        # comm_ss = ['java', '-cp', '/home1/08440/tg877399/BottleneckDetection/dataset_generator/utilities/', 'SimpleSender1',
        #            dst_ip, port_number, src_path, str(label_value)]
        strings = ""
        proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
        # pid = check_output(['/sbin/pidof', '-s', 'java', 'SimpleSender1.java'])
        # pid = check_output(['/bin/pidof', '-s', 'java', 'SimpleSender1.java'])
        global_vars.pid = str(proc.pid)
        print(global_vars.pid)
        global_vars.sender_process = psutil.Process(proc.pid)
        # global label_value
        # output_file.write("label = " + str(label_value) + "\n")
        # output_file.write("start time = " + time.ctime() + "\n")
        # output_file.flush()
        # output_file.close
        # while (True):
        #    pass
        #     line = str(proc.stdout.readline()).replace("\r", "\n")
        #     strings += line
        # if not line.decode("utf-8"):
        #     break
        # strings.replace("\r", "\n")
