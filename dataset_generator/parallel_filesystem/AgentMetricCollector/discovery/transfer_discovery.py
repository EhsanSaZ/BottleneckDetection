import re
import subprocess
import threading
import traceback
import time


class TransferDiscovery(threading.Thread):
    def __init__(self, local_ip_addr, local_port_range, peer_ip_addr, peer_port_range,
                 transfer_validator, transfer_manager, discovery_cycle=1):
        threading.Thread.__init__(self)
        self.local_ip_addr = local_ip_addr
        self.local_port_range = local_port_range
        self.peer_ip_addr = peer_ip_addr
        self.peer_port_range = peer_port_range
        self.running_transfers = {}
        self.monitored_transfers = {}
        self.transfer_validator = transfer_validator
        self.discovery_cycle = discovery_cycle
        self.transfer_manager = transfer_manager

    def is_transfer_valid(self, local_address_ip, local_address_port, peer_address_ip, peer_address_port):
        if local_address_ip == self.local_ip_addr and self.local_port_range[0] <= int(local_address_port) <= \
                self.local_port_range[1] \
                and peer_address_ip == self.peer_ip_addr and self.peer_port_range[0] <= int(
            peer_address_port) <= \
                self.peer_port_range[1]:
            return True
        else:
            return False

    @staticmethod
    def extract_ip_port(text):
        ip_port_match_re = r"(?P<ip_part>.*):(?P<port_part>\d*)"
        ipv4_re = r"(?P<ipv4>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)"
        ip_port_match = re.search(ip_port_match_re, text)
        if ip_port_match:
            ip_part = ip_port_match.groupdict().get("ip_part")
            ipv4_match = re.search(ipv4_re, ip_part)
            ip = ipv4_match.groupdict().get("ipv4") or ""
            port = ip_port_match.groupdict().get("port_part") or "-1"
            return ip, port
        else:
            return None, None

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
                for i in range(len(lines)):
                    if self.local_ip_addr in lines[i] and self.peer_ip_addr in lines[i]:
                        # if True:
                        first_parts = lines[i].split(" ")
                        first_list = []
                        for item in first_parts:
                            if len(item.strip()) > 0:
                                first_list.append(item)
                        # receiver_buffer_value = int(first_list[0].strip())
                        # send_buffer_value = int(first_list[1].strip())
                        sender_ip, sender_port = self.extract_ip_port(first_list[2])
                        receiver_ip, receiver_port = self.extract_ip_port(first_list[3])

                        if self.transfer_validator.is_transfer_valid(sender_ip, sender_port,
                                                                     receiver_ip, receiver_port,
                                                                     self.local_ip_addr, self.local_port_range,
                                                                     self.peer_ip_addr,
                                                                     self.peer_port_range) and len(first_list) == 5:
                            # print(self.is_transfer_valid(sender_ip, sender_port, receiver_ip, receiver_port), first_list)
                            match = re.search(r"pid=(\d*),", first_list[4])
                            if match:
                                pid = int(match[1])
                                # print("Find transfer", pid, sender_ip, sender_port, receiver_ip, receiver_port)
                                self.running_transfers[pid] = {"pid": pid, "local_ip": sender_ip,
                                                               "local_port": sender_port,
                                                               "peer_ip": receiver_ip,
                                                               "peer_port": receiver_port}
                new_transfers = set(self.running_transfers.keys()) - set(self.monitored_transfers.keys())
                ended_transfers = set(self.monitored_transfers.keys()) - set(self.running_transfers.keys())
                for tr in new_transfers:
                    print("Adding new transfer", self.running_transfers[tr])
                    self.transfer_manager.add_new_monitoring_thread(self.running_transfers[tr])
                    self.monitored_transfers[tr] = self.running_transfers[tr]
                for tr in ended_transfers:
                    print("Removing ended transfer", self.monitored_transfers[tr])
                    self.transfer_manager.stop_monitoring_thread(self.monitored_transfers[tr])
                    del self.monitored_transfers[tr]
                time.sleep(self.discovery_cycle)
        except Exception as e:
            traceback.print_exc()

    def run(self):
        self.start_discovery()
