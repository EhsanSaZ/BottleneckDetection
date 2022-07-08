import subprocess
import threading

import psutil

import remote_global_vars


class RunServerThread(threading.Thread):
    def __init__(self, name, java_receiver_app_path, server_saving_directory, server_port_number,
                 java_server_throughput_label):
        threading.Thread.__init__(self)
        self.name = name
        self.java_receiver_app_path = java_receiver_app_path
        self.server_saving_directory = server_saving_directory
        self.server_port_number = server_port_number
        self.java_server_throughput_label = java_server_throughput_label

    def run(self):
        print("\nStarting " + self.name)
        self.run_server(self.name)
        print("\nExiting " + self.name)

    def run_server(self, i):
        # global pid, label_value, server_process

        comm_ss = ['java', self.java_receiver_app_path, self.server_saving_directory, server_port_number,
                   self.java_server_throughput_label]
        proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)

        # pid = check_output(['/sbin/pidof', '-s', 'java', 'SimpleReceiver1.java'])
        # pid = check_output(['/bin/pidof', '-s', 'java', 'SimpleReceiver1.java'])
        remote_global_vars.pid = str(proc.pid)
        print(remote_global_vars.pid)
        remote_global_vars.server_process = psutil.Process(proc.pid)
        # global label_value
        # strings = ""
        # while (True):
        #     line = str(sender_process.stdout.readline()).replace("\r", "\n")
        #     strings += line
        #     # if not line.decode("utf-8"):
        #     #     break
        #     strings.replace("\r", "\n")