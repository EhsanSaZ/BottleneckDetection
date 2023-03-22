import json
import os
import sys
import threading
import time
import traceback
import psutil
import zmq
import hashlib
from datetime import datetime, timezone
from subprocess import Popen, PIPE

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
from collectors.network_metric_collector_ss_v2 import NetworkMetricCollectorSS_V2
from collectors.system_metric_collector import SystemMetricCollector
# from collectors.file_ost_path_info import FileOstPathInfo
from collectors.file_ost_path_info_v2 import FileOstPathInfoV2
# from collectors.file_mdt_path_info import FileMdtPathInfo
from collectors.file_mdt_path_info_v2 import FileMdtPathInfoV2
from collectors.client_ost_metric_collector import ClientOstMetricCollector
# from collectors.client_ost_metric_zmq_collector import ClientOstMetricZmqCollector
# from collectors.client_mdt_metric_collector import ClientMdtMetricCollector
# from collectors.client_mdt_metric_zmq_collector import ClientMdtMetricZmqCollector
# from collectors.lustre_ost_metric_http_collector import LustreOstMetricHttpCollector
from collectors.lustre_ost_metric_zmq_collector import LustreOstMetricZmqCollector
from collectors.protobuf_messages.log_metrics_pb2 import Metrics, MonitoringLog, PublisherPayload, ResourceUsageMetrics, BufferValueMetrics
from helper_threads import fileWriteThread
from Config import Config
# import system_monitoring_global_vars
import global_vars
from helper_threads import overheadFileWriteThread
from multiprocessing import Process, Event

class StatProcess(Process):
    def __init__(self, src_ip, src_port, dst_ip, dst_port, zmq_context,
                 xsub_backend_socket_name,
                 ost_metric_backend_socket_name,
                 client_ost_metric_backend_socket_name,
                 remote_ost_index_to_ost_agent_http_address_dict,
                 pid_str, path,
                 mdt_parent_path, label_value, is_sender,
                 write_thread_directory, over_head_write_thread_directory, ready_to_publish,
                 cpu_mem_dict, buffer_value_dict,
                 client_ost_metrics_dict,
                system_lustre_nic_io_dict, **kwargs):
        # threading.Thread.__init__(self)
        super(StatProcess, self).__init__(**kwargs)
        self._stop = Event()
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.ost_metric_backend_socket_name = ost_metric_backend_socket_name
        self.client_ost_metric_backend_socket_name = client_ost_metric_backend_socket_name
        # self.client_mdt_metric_backend_socket_name = client_mdt_metric_backend_socket_name
        self.remote_ost_index_to_ost_agent_http_address_dict = remote_ost_index_to_ost_agent_http_address_dict
        self.pid_str = pid_str
        self.file_path = path
        self.is_transfer_done = False
        self.mdt_parent_path = mdt_parent_path
        self.label_value = label_value
        self.is_sender = is_sender
        self.prefix = "sender_" if self.is_sender else "receiver_"
        self.write_thread_directory = write_thread_directory
        self.over_head_write_thread_directory = over_head_write_thread_directory
        self.ready_to_publish = ready_to_publish
        self.cpu_mem_dict = cpu_mem_dict
        self.buffer_value_dict = buffer_value_dict
        self.client_ost_metrics_dict = client_ost_metrics_dict
        # self.client_mdt_metrics_dict = client_mdt_metrics_dict
        # self.dtn_io_metrics_dict = dtn_io_metrics_dict
        self.system_lustre_nic_io_dict = system_lustre_nic_io_dict
        self.latest_file_name = None
        self.latest_ost_path_output = None
        self.latest_mdt_path_output = None
        self.latest_file_mount_point = None
        self.monitoring_agent = psutil.Process(int(global_vars.monitor_agent_pid.value))

    def run(self):
        self.collect_stat()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run_monitor_commands(self):

        seperator = '--result--'
        command_seperator = '--command_result--'
        network_metrics_command = "ss -it state ESTABLISHED src {}:{} dst {}:{}".format(self.src_ip, self.src_port,
                                                                                        self.dst_ip, self.dst_port)
        # system_metrics_command = "cat /proc/{pid}/io; echo {seperator}; cat /proc/{pid}/stat".format(pid=self.pid_str,
        #                                                                                              seperator=seperator)
        read_fd_command = "ls -l /proc/{pid}/fd/".format(pid=self.pid_str)
        all_commands = "{} ; echo {seperator}; {}".format(network_metrics_command,read_fd_command, seperator=command_seperator)
        proc = Popen(all_commands, shell=True, universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split(command_seperator)
        network_output = res_parts[0]
        # system_output = res_parts[1]
        fd_output = res_parts[1]
        return network_output, fd_output
    def run_ost_mdt_path_info_commands(self, pid,  lustre_mnt_point_list, fd_output=None):
        seperator = '--result--'
        command_seperator = '--command_result--'
        if fd_output:
            res = fd_output
        else:
            proc = Popen(['ls', '-l', '/proc/' + str(int(pid.strip())) + '/fd/'], universal_newlines=True, stdout=PIPE)
            # total 0
            # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 0 -> /dev/pts/98
            # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 1 -> /dev/pts/98
            # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 2 -> /dev/pts/98
            # lr-x------ 1 ehsansa sub102 64 Nov 22 14:09 3 -> /home/ehsansa/sample_text.txt
            res = proc.communicate()[0]
        res_parts = res.split("\n")
        for line in res_parts:
            if len(line.strip()) > 0:
                for mnt_path in lustre_mnt_point_list:
                    if mnt_path in line:
                        # lr-x------ 1 ehsansa sub102 64 Nov 22 14:09 3 -> /home/ehsansa/sample_text.txt
                        slash_index = line.rfind(">")

                        file_name = line[slash_index + 1:].strip()
                        first_slash_index = file_name.find("/")
                        second_slash_index = file_name.find("/", first_slash_index + 1)
                        file_mount_point = file_name[first_slash_index + 1: first_slash_index + second_slash_index]
                        if self.latest_file_name != file_name:
                            self.latest_file_name = file_name
                            ost_path_info_cmd = "lfs getstripe {file_name}; echo {seperator}; ls -l /sys/kernel/debug/lustre/osc".format(file_name=file_name, seperator=seperator)
                            # mdt_path_info_cmd = "lfs getstripe -m {file_name}; echo {seperator}; ls -l /sys/kernel/debug/lustre/mdc/".format(file_name=file_name, seperator=seperator)
                            all_commands = "{} ;".format(ost_path_info_cmd, seperator=command_seperator)

                            proc = Popen(all_commands, shell=True, universal_newlines=True, stdout=PIPE)
                            all_res = proc.communicate()[0]
                            all_res_parts = all_res.split(command_seperator)
                            # ost_path_output = all_res_parts[0]
                            # mdt_path_output = all_res_parts[1]
                            self.latest_ost_path_output = all_res_parts[0]
                            # self.latest_mdt_path_output = all_res_parts[1]
                            self.latest_file_mount_point = file_mount_point
                        return self.latest_ost_path_output, self.latest_file_mount_point

        return None, None
    def collect_stat(self):
        # import cProfile
        # import pstats, math
        # import io
        # import pandas as pd
        # pr = cProfile.Profile()
        # pr.enable()
        # self.profile_name = str(self.pid)
        is_parallel_file_system = False
        proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        parts = res.split("\n")
        for x in parts:
            if "lustre" in x:
                is_parallel_file_system = True

        network_metrics_collector = NetworkMetricCollectorSS_V2(self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.prefix)
        file_ost_path_info_extractor = FileOstPathInfoV2()
        # file_mdt_path_info_extractor = FileMdtPathInfoV2()
        client_ost_metrics_collector = ClientOstMetricCollector(self.prefix)
        lustre_ost_metrics_zmq_collector = LustreOstMetricZmqCollector(self.context, self.ost_metric_backend_socket_name, self.prefix)
        # TO DO REMOVE THIS LINE ITS JUST A TEST
        # is_parallel_file_system = True

        is_first_time = True
        time_diff = 0
        epoc_time = 0
        sleep_time = 1
        epoc_count = 0
        overhead_epoc_count = 0
        main_output_string = ""
        overhead_main_output_string = ""

        data_transfer_overhead = 0
        metric_publisher_socket = None
        if Config.send_to_cloud_mode:
            metric_publisher_socket = self.context.socket(zmq.PUB)
            metric_publisher_socket.connect("ipc://{}".format(self.xsub_backend_socket_name))
        target_process = None
        try:
            target_process = psutil.Process(int(self.pid_str))
        except psutil.NoSuchProcess as e:
            print(e.msg)
            print("Exiting Collect Stat Thread. Process not found")
            self.is_transfer_done = True
        transfer_id = None
        while 1:
            processing_start_date = datetime.now(tz=timezone.utc)
            processing_start_timestampt = datetime.timestamp(processing_start_date)
            # processing_start_timestampt = time.time()
            # print("COLLECTING", transfer_id, processing_start_time)

            if self.is_transfer_done or self.stopped():
                break

            try:
                if (is_first_time):
                    # Create tid here...
                    discovery_time = datetime.now().strftime('%Y-%m-%d_%H:%M')
                    if self.is_sender:
                        id_str = "{}_{}_{}_{}_{}".format(discovery_time, self.src_ip, self.src_port, self.dst_ip,
                                                         self.dst_port)
                    else:
                        id_str = "{}_{}_{}_{}_{}".format(discovery_time, self.dst_ip, self.dst_port, self.src_ip,
                                                         self.src_port)
                    transfer_id = hashlib.md5(id_str.encode('utf-8')).hexdigest()
                    print(transfer_id, os.getpid())
                    # TODO
                    # Send a request to the realtime detection service to add this new transfer
                time_diff += 1
                # epoc_time += 1
                network_output, fd_output = self.run_monitor_commands()
                network_metrics_collector.collect_metrics(from_string=network_output)
                # system_metrics_collector.collect_metrics(self.pid_str, target_process, from_string=system_output)
                if is_parallel_file_system:
                    ost_path_output, file_mount_point = self.run_ost_mdt_path_info_commands(self.pid_str, self.file_path, fd_output=fd_output)
                    # print(ost_path_output, mdt_path_output)

                    # file_ost_path_info = file_ost_path_info_extractor.get_file_ost_path_info(self.pid_str, self.file_path, from_string=fd_output)
                    file_ost_path_info = file_ost_path_info_extractor.get_file_ost_path_info(file_mount_point, from_string=ost_path_output)
                    if file_ost_path_info is None:
                        time.sleep(0.1)
                        continue
                    else:
                        ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = file_ost_path_info
                    # print(ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number)
                    client_ost_metrics_collector.collect_metrics(ost_dir_name, int(processing_start_timestampt), self.client_ost_metrics_dict.get(ost_dir_name))

                    lustre_ost_metrics_zmq_collector.collect_metrics(ost_number, remote_ost_dir_name, int(processing_start_timestampt))

                epoc_count += 1
                # print(output_string)
                time_second = processing_start_timestampt
                if Config.send_to_cloud_mode and Config.communication_type == "JSON" and not is_first_time and self.ready_to_publish:
                    epoc_time += 1
                    data = {}
                    # print(transfer_id)
                    metrics_data = {"time_stamp": str(time_second)}
                    metrics_data.update(network_metrics_collector.get_metrics_dict())
                    # TODO Update this  system_monitoring_global_vars
                    for key in self.cpu_mem_dict.keys():
                        metrics_data["{}{}".format(self.prefix, key)] = self.cpu_mem_dict[key]
                    # for key in self.buffer_value_dict.keys():
                    for key in ["tcp_rcv_buffer_max", "tcp_snd_buffer_max"]:
                        metrics_data["{}{}".format(self.prefix, key)] = self.buffer_value_dict[key]
                    metrics_data.update(client_ost_metrics_collector.get_metrics_dict())
                    # TODO Update this  system_monitoring_global_vars
                    for key in self.system_lustre_nic_io_dict.keys():
                        metrics_data["{}{}".format(self.prefix, key)] = self.system_lustre_nic_io_dict[key]
                    metrics_data.update(lustre_ost_metrics_zmq_collector.get_metrics_dict())
                    metrics_data.update({"label_value": self.label_value})

                    data["transfer_ID"] = transfer_id
                    data["data"] = metrics_data
                    data["sequence_number"] = epoc_time
                    data["is_sender"] = self.is_sender
                    body = json.dumps(data)
                    # print(transfer_id, metrics_data)
                    # data_transfer_overhead = len(body.encode('utf-8'))
                    metric_publisher_socket.send_json(body)
                elif Config.send_to_cloud_mode and Config.communication_type == "PROTO" and not is_first_time and self.ready_to_publish:
                    epoc_time += 1
                    ts = datetime.fromtimestamp(float(processing_start_timestampt), tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')
                    metrics = ""
                    metrics += network_metrics_collector.get_metrics_str()
                    for key in self.cpu_mem_dict.keys():
                        metrics += "," + self.cpu_mem_dict[key]
                    # for key in self.buffer_value_dict.keys():
                    for key in ["tcp_rcv_buffer_max", "tcp_snd_buffer_max"]:
                        metrics += "," + self.buffer_value_dict[key]
                    metrics += "," + client_ost_metrics_collector.get_metrics_str()
                    for key in self.system_lustre_nic_io_dict.keys():
                        metrics += "," + self.system_lustre_nic_io_dict[key]
                    metrics += "," + lustre_ost_metrics_zmq_collector.get_metrics_str()
                    metrics += "," + self.label_value
                    msg = "{time} {tid} {sender} {metrics}".format(time=ts, tid=transfer_id, sender=self.is_sender, metrics=metrics)
                    # data_transfer_overhead = len(msg.encode('utf-8'))
                    metric_publisher_socket.send_string(msg)
                    # metric_publisher_socket.send(log_data_request.SerializeToString())
                elif not is_first_time:
                    epoc_time += 1
                    # output_string = str(time_second)
                    metrics = ""
                    metrics += network_metrics_collector.get_metrics_str()
                    for key in self.cpu_mem_dict.keys():
                        metrics += "," + self.cpu_mem_dict[key]
                    # for key in self.buffer_value_dict.keys():
                    for key in ["tcp_rcv_buffer_max", "tcp_snd_buffer_max"]:
                        metrics += "," + self.buffer_value_dict[key]
                    metrics += "," + client_ost_metrics_collector.get_metrics_str()
                    for key in self.system_lustre_nic_io_dict.keys():
                        metrics += "," + self.system_lustre_nic_io_dict[key]
                    metrics += "," + lustre_ost_metrics_zmq_collector.get_metrics_str()
                    metrics += "," + self.label_value + "\n"
                    output_string = "{},{}".format(str(time_second), metrics)
                    main_output_string += output_string
                    if epoc_count % 5 == 0:
                        print("transferring file.... ", epoc_count, "label: ", self.label_value)
                        if epoc_count % 100 == 0:
                            print("transferring file.... ", epoc_count, "label: ", self.label_value)
                            epoc_count = 0
                        # write_thread = fileWriteThread(main_output_string, "./sender/logs/dataset_", self.label_value)
                        # write_thread = fileWriteThread(main_output_string, "./receiver/logs/dataset_",self.label_value)
                        write_thread = fileWriteThread(main_output_string, self.write_thread_directory, self.label_value)
                        write_thread.start()
                        main_output_string = ""
                else:
                    # print("skip first transfer")
                    is_first_time = False
            except psutil.NoSuchProcess as e:
                print(e.msg)
                print("EXITNG COLLECT STAT THREAD for {}".format(transfer_id))
                self.is_transfer_done = True
            except:
                print("EXITNG COLLECT STAT THREAD for {}".format(transfer_id))
                traceback.print_exc()
            processing_finish_date = datetime.now(tz=timezone.utc)
            processing_finish_time = datetime.timestamp(processing_finish_date)
            # processing_finish_time = time.time()
            processing_time = processing_finish_time - processing_start_timestampt
            # # cpu_memory_overhead = agent_resource_usage_collector.get_process_io_stats(global_vars.monitor_agent_pid,
            # #                                                                           global_vars.monitor_agent_process)
            # overhead_output_string = "{},{},{},{},{}\n".format(processing_finish_time,
            #                                                    processing_time,
            #                                                    data_transfer_overhead,
            #                                                    self.monitoring_agent.cpu_percent(),
            #                                                    self.monitoring_agent.memory_percent())
            # overhead_epoc_count += 1
            # if not is_first_time:
            #     overhead_main_output_string += overhead_output_string
            #     if overhead_epoc_count % 10 == 0:
            #         overhead_epoc_count = 0
            #         overhead_write = overheadFileWriteThread("./sender/overhead_logs/overhead_footprints.csv", overhead_main_output_string)
            #         overhead_write = overheadFileWriteThread("./receiver/overhead_logs/overhead_footprints.csv",overhead_main_output_string)
            #         overhead_write = overheadFileWriteThread(overhead_main_output_string, self.over_head_write_thread_directory)
            #         overhead_write.start()
            #         overhead_main_output_string = ""
            # time.sleep(min(sleep_time, abs(sleep_time - processing_time)))
            time.sleep(abs(sleep_time - (processing_time % sleep_time)))
        # pr.disable()
        # result = io.StringIO()
        # pstats.Stats(pr,stream=result).print_stats()
        # result=result.getvalue()
        # # chop the string into a csv-like buffer
        # result='ncalls'+result.split('ncalls')[-1]
        # result='\n'.join([','.join(line.rstrip().split(None,5)) for line in result.split('\n')])
        # # save it to disk
        #
        # with open('{}_profile_data.csv'.format(self.profile_name), 'w+') as f:
        #     #f=open(result.rsplit('.')[0]+'.csv','w')
        #     f.write(result)
        #     f.close()