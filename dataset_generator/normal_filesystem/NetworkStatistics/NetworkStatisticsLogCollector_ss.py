import re
import subprocess


class NetworkStatisticsLogCollectorSS:
    def __init__(self, destination_ip, destination_port):
        self.send_buffer_value = 0
        self.data_segs_out = 0
        self.data_seg_out_so_far = 0
        self.total_rto_value = 0
        self.total_rtt_value = 0
        self.total_mss_value = 0
        self.total_cwnd_value = 0
        self.total_ssthresh_value = 0
        self.byte_ack = 0
        self.byte_ack_so_far = 0
        self.segs_out = 0
        self.seg_out_so_far = 0
        self.segs_in = 0
        self.segs_in_sofar = 0
        self.send = 0
        self.total_pacing_rate = 0
        self.unacked = 0
        self.retrans = 0
        self.retrans_so_far = 0
        self.rcv_space = 0
        self.dsack_dups = 0
        self.dsack_dups_so_far = 0
        self.reord_seen = 0
        self.reord_seen_so_far = 0

        self.line_in_ss = ""
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def execute_command(self):
        comm_ss = ['ss', '-t', '-i', 'state', 'ESTABLISHED', 'dst', self.destination_ip + ":" + self.destination_port]
        ss_proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
        self.line_in_ss = str(ss_proc.stdout.read())

    def parse_output(self):
        if self.line_in_ss.count(self.destination_ip) >= 1:
            parts = self.line_in_ss.split("\\n")

            for x in range(len(parts)):
                if self.destination_ip in parts[x] and self.destination_port in parts[x]:
                    first_parts = parts[x].split(" ")
                    first_list = []
                    for item in first_parts:
                        if len(item.strip()) > 0:
                            first_list.append(item)
                    # T ODO WHAT INDEX IS CORRECT?
                    #  WHAT is the output of ss -t -i command?
                    self.send_buffer_value = int(first_list[1].strip())
                    # send_buffer_value = int(first_list[7].strip())
                    # send_buffer_value = int(first_list[-3].strip())
                    # print (first_list)
                    metrics_line = parts[x + 1].strip("\\t").strip()
                    metrics_parts = metrics_line.split(" ")
                    for y in range(len(metrics_parts)):
                        if re.search(r'\bdata_segs_out\b', metrics_parts[y]):
                            pass
                            # s_index = metrics_parts[y].find(":")
                            # value = float(metrics_parts[y][s_index+1:])
                            # self.data_segs_out=(value-data_seg_out_so_far)
                            # self.data_seg_out_so_far = value
                        elif re.search(r'\brto\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.total_rto_value = value
                        elif re.search(r'\brtt\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            e_index = metrics_parts[y].find("/")
                            value = float(metrics_parts[y][s_index + 1:e_index])
                            self.total_rtt_value = value
                        elif re.search(r'\bmss\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            # print("value ",value)
                            self.total_mss_value = value
                        elif re.search(r'\bcwnd\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.total_cwnd_value = value
                        elif re.search(r'\bssthresh\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.total_ssthresh_value = value
                        elif re.search(r'\bbytes_acked\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.byte_ack = (value - self.byte_ack_so_far)
                            self.byte_ack_so_far = value
                        elif re.search(r'\bsegs_out\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            # print("value ", value)
                            # print("seg_out_so_far ", seg_out_so_far)
                            self.segs_out = (value - self.seg_out_so_far)
                            self.seg_out_so_far = value
                        elif re.search(r'\bsegs_in\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.segs_in = (value - self.segs_in_sofar)
                            self.segs_in_sofar = value
                        elif re.search(r'\bsend\b', metrics_parts[y]):
                            value = metrics_parts[y + 1].strip()
                            self.send = value
                        elif re.search(r'\bpacing_rate\b', metrics_parts[y]):
                            value = metrics_parts[y + 1].strip()
                            self.total_pacing_rate = value
                        elif re.search(r'\bunacked\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.unacked = value
                        elif re.search(r'\bretrans\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find("/")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.retrans = value - self.retrans_so_far
                            self.retrans_so_far = value
                        elif re.search(r'\brcv_space\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.rcv_space = value
                        elif re.search(r'\bdsack_dups\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.dsack_dups = value - self.dsack_dups_so_far
                            self.dsack_dups_so_far = value
                        elif re.search(r'\breord_seen\b', metrics_parts[y]):
                            s_index = metrics_parts[y].find(":")
                            value = float(metrics_parts[y][s_index + 1:])
                            self.reord_seen = value - self.reord_seen_so_far
                            self.reord_seen_so_far = value

    def get_log_str(self):
        self.execute_command()
        self.parse_output()

        return str(self.total_rtt_value) + "," + str(self.total_pacing_rate) + "," + str(
            self.total_cwnd_value) + "," + str(self.total_rto_value) + "," + \
               str(self.byte_ack / (1024 * 1024)) + "," + str(self.segs_out) + "," + str(self.retrans) + "," + \
               str(self.total_mss_value) + "," + str(self.total_ssthresh_value) + "," + str(self.segs_in) + "," + \
               str(self.send) + "," + str(self.unacked) + "," + str(self.rcv_space) + "," + \
               str(self.send_buffer_value)

