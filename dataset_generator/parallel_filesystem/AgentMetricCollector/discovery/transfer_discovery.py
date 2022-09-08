import hashlib
import re
import subprocess
import threading
import traceback
import time
from multiprocessing import Process

class TransferDiscovery(Process):
    def __init__(self, local_ip_addr_list, peer_ip_addr_list,
                 send_port_range, receive_port_range,
                 transfer_validator, transfer_manager, discovery_cycle=1, **kwargs):
        # threading.Thread.__init__(self)
        super(TransferDiscovery, self).__init__(**kwargs)
        self.local_ip_addr_list = local_ip_addr_list
        self.peer_ip_addr_list = peer_ip_addr_list
        self.send_port_range = send_port_range
        self.receive_port_range = receive_port_range
        self.running_transfers = {}
        self.monitored_transfers = {}
        self.transfer_validator = transfer_validator
        self.discovery_cycle = discovery_cycle
        self.transfer_manager = transfer_manager

    @staticmethod
    def extract_ip_port(text):
        ip_port_match_re = r"(?P<ip_part>.*):(?P<port_part>\d*)"
        ipv4_re = r"(?P<ipv4>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)"
        ip_port_match = re.search(ip_port_match_re, text)
        if ip_port_match:
            ip_part = ip_port_match.groupdict().get("ip_part")
            ipv4_match = re.search(ipv4_re, ip_part)
            if ipv4_match:
                ip = ipv4_match.groupdict().get("ipv4") or ""
                port = ip_port_match.groupdict().get("port_part") or "-1"
                return ip, port
            else:
                return None, None
        else:
            return None, None

    def process_running_transfers(self):
        new_transfers = set(self.running_transfers.keys()) - set(self.monitored_transfers.keys())
        ended_transfers = set(self.monitored_transfers.keys()) - set(self.running_transfers.keys())
        for tr in new_transfers:
            if self.transfer_validator.in_range(int(self.running_transfers[tr]["local_port"]), self.send_port_range):
                print("Adding new sender transfer", self.running_transfers[tr])
                self.transfer_manager.add_new_monitoring_process(self.running_transfers[tr], is_sender=1,
                                                                 dataset_path="./sender/logs/dataset_",
                                                                 overhead_log_path="./sender/overhead_logs/overhead_footprints.csv")
            elif self.transfer_validator.in_range(int(self.running_transfers[tr]["local_port"]),
                                                  self.receive_port_range):
                print("Adding new receive transfer", self.running_transfers[tr])
                self.transfer_manager.add_new_monitoring_process(self.running_transfers[tr], is_sender=0,
                                                                 dataset_path="./receiver/logs/dataset_",
                                                                 overhead_log_path="./receiver/overhead_logs/overhead_footprints.csv")
            self.monitored_transfers[tr] = self.running_transfers[tr]
        for tr in ended_transfers:
            print("Removing ended transfer", self.monitored_transfers[tr])
            self.transfer_manager.stop_monitoring_process(self.monitored_transfers[tr])
            del self.monitored_transfers[tr]

    def start_discovery(self):
        try:
            comm_ss = ['ss', '-t', '-i', '-p', 'state', 'ESTABLISHED']
            while True:
                self.running_transfers = {}
                ss_proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
                line_in_ss = str(ss_proc.stdout.read())
                lines = line_in_ss.split("\\n")
                # print(lines[0])
                lines = lines[1:]
                for i in range(0, len(lines), 2):
                    first_parts = lines[i].split(" ")
                    first_list = []
                    for item in first_parts:
                        if len(item.strip()) > 0:
                            first_list.append(item)
                    if len(first_list) == 5:
                        # receiver_buffer_value = int(first_list[0].strip())
                        # send_buffer_value = int(first_list[1].strip())
                        transfer_local_ip, transfer_local_port = self.extract_ip_port(first_list[2])
                        transfer_peer_ip, transfer_peer_port = self.extract_ip_port(first_list[3])

                        if self.transfer_validator.is_transfer_valid(transfer_local_ip, transfer_local_port,
                                                                     transfer_peer_ip, transfer_peer_port,
                                                                     self.local_ip_addr_list,
                                                                     self.peer_ip_addr_list,
                                                                     self.send_port_range,
                                                                     self.receive_port_range) and len(first_list) == 5:
                            match = re.search(r"pid=(\d*),", first_list[4])
                            if match:
                                pid = int(match[1])
                                # print("Find transfer", pid, sender_ip, sender_port, receiver_ip, receiver_port)
                                id_str = "{}-{}-{}-{}-{}".format(pid,
                                                                 transfer_local_ip, transfer_local_port,
                                                                 transfer_peer_ip, transfer_peer_port)
                                id_hashed = hashlib.md5(id_str.encode('utf-8')).hexdigest()
                                self.running_transfers[id_hashed] = {"pid": pid, "local_ip": transfer_local_ip,
                                                               "local_port": transfer_local_port,
                                                               "peer_ip": transfer_peer_ip,
                                                               "peer_port": transfer_peer_port}
                self.process_running_transfers()
                time.sleep(self.discovery_cycle)
        except Exception as e:
            traceback.print_exc()

    def run(self):
        self.start_discovery()
