import copy
import hashlib
import json
import threading
import time
import traceback
from subprocess import Popen, PIPE

import psutil
import zmq

import system_monitoring_global_vars
from RemoteNetworkStatistics.RemoteNetworkStatisticsLogCollector_ss import RemoteNetworkStatisticsLogCollectorSS
from helper_threads import fileWriteThread, overheadFileWriteThread
from statistics_log_collector import StatisticsLogCollector
from data_converter import DataConverter
from Config import Config
from datetime import datetime


class RemoteStatThread(threading.Thread):
    def __init__(self, server_ip, server_port_number, client_ip, client_port, zmq_context,
                 xsub_backend_socket_name,
                 remote_ost_index_to_ost_agent_address_dict, pid_str, server_saving_directory,
                 mdt_parent_path, label_value):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.server_ip = server_ip
        self.server_port_number = server_port_number
        self.client_ip = client_ip
        self.client_port = client_port
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.remote_ost_index_to_ost_agent_address_dict = remote_ost_index_to_ost_agent_address_dict
        self.pid_str = pid_str
        self.server_saving_directory = server_saving_directory
        self.is_transfer_done = False
        self.mdt_parent_path = mdt_parent_path
        self.label_value = label_value

    def run(self):
        self.collect_stat()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    # def collect_stat(self):
    #     while 1:
    #         if self.stopped():
    #             return
    #         print("collecting status")
    #         time.sleep(1)

    def collect_stat(self):
        is_parallel_file_system = False
        proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        parts = res.split("\n")
        for x in parts:
            if "lustre" in x:
                is_parallel_file_system = True

        network_statistics_collector = RemoteNetworkStatisticsLogCollectorSS(self.server_ip, self.server_port_number,
                                                                             self.client_ip, self.client_port)
        remote_statistics_collector = StatisticsLogCollector()
        data_converter = DataConverter(file_system="lustre", prefix="receiver_")
        # T ODO REMOVE THIS LINE ITS JUST A TEST
        # is_parallel_file_system = True

        if is_parallel_file_system:
            mdt_paths = []
            mdt_stat_so_far_general = {"req_waittime": 0.0, "req_active": 0.0, "mds_getattr": 0.0,
                                       "mds_getattr_lock": 0.0, "mds_close": 0.0, "mds_readpage": 0.0,
                                       "mds_connect": 0.0, "mds_get_root": 0.0, "mds_statfs": 0.0,
                                       "mds_sync": 0.0, "mds_quotactl": 0.0, "mds_getxattr": 0.0,
                                       "mds_hsm_state_set": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0,
                                       "seq_query": 0.0, "fld_query": 0.0,
                                       "md_stats": {
                                           "close": 0.0, "create": 0.0, "enqueue": 0.0, "getattr": 0.0,
                                           "intent_lock": 0.0,
                                           "link": 0.0, "rename": 0.0, "setattr": 0.0, "fsync": 0.0, "read_page": 0.0,
                                           "unlink": 0.0, "setxattr": 0.0, "getxattr": 0.0,
                                           "intent_getattr_async": 0.0, "revalidate_lock": 0.0
                                       }}
            all_mdt_stat_so_far_dict = {}
            proc = Popen(['ls', '-l', self.mdt_parent_path], universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split("\n")
            for line in res_parts:
                if len(line.strip()) > 0:
                    if "total" not in line:
                        parts = line.split(" ")
                        # print(parts)
                        mdt_paths.append(parts[-1])
                        all_mdt_stat_so_far_dict[parts[-1]] = copy.deepcopy(mdt_stat_so_far_general)

            is_first_time = True
            time_diff = 0
            epoc_time = 0
            sleep_time = 1
            epoc_count = 0
            overhead_epoc_count = 0
            main_output_string = ""
            overhead_main_output_string = ""
            ost_stats_so_far = {"req_waittime": 0.0, "req_active": 0.0, "read_bytes": 0.0, "write_bytes": 0.0,
                                "ost_setattr": 0.0, "ost_read": 0.0, "ost_write": 0.0, "ost_get_info": 0.0,
                                "ost_connect": 0.0, "ost_punch": 0.0, "ost_statfs": 0.0, "ost_sync": 0.0,
                                "ost_quotactl": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0}
            #
            all_remote_ost_stats_so_far = {}
            data_transfer_overhead = 0
            metric_publisher_socket = None
            if Config.send_to_cloud_mode:
                metric_publisher_socket = self.context.socket(zmq.PUB)
                metric_publisher_socket.connect("inproc://{}".format(self.xsub_backend_socket_name))
            server_process = None
            try:
                server_process = psutil.Process(int(self.pid_str))
            except psutil.NoSuchProcess as e:
                print(e.msg)
                print("Exiting Collect Stat Thread. Process not found")
                self.is_transfer_done = True

            while 1:
                processing_start_time = time.time()
                ### NETWORK METRICS ###

                if self.is_transfer_done or self.stopped():
                    break
                # If the pid is 0, then the transfer thread is not started yet or the global pid is not updated yet
                # So it is not possible to collect for system metrics, then just skip this iteration

                # if not network_statistics_collector.check_established_connection_exist():  # or pid == 0
                #     epoc_time = 0
                #     time.sleep(0.1)
                #     continue
                try:
                    # print("COLLECT")
                    if is_first_time:
                        discovery_time = datetime.now().strftime('%Y-%m-%d_%H:%M')
                        sender_ip = ""
                        sender_port = ""
                        receiver_ip = ""
                        receiver_port = ""
                        id_str = "{}_{}_{}_{}_{}".format(discovery_time, sender_ip, sender_port, receiver_ip,
                                                         receiver_port)
                        transfer_id = hashlib.md5(id_str.encode('utf-8')).hexdigest()
                        initial_time = time.time()
                        # Send a request to the realtime detection service to add this new transfer
                    time_diff += 1
                    # epoc_time += 1

                    if time_diff >= (.1 / sleep_time):
                        system_value_list = remote_statistics_collector.collect_system_metrics(self.pid, server_process)
                        buffer_value_list = remote_statistics_collector.get_buffer_value()
                        # ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = collect_file_ost_path_info(self.pid, src_path)
                        file_ost_path_info = remote_statistics_collector.collect_file_ost_path_info(
                            self.pid,
                            self.server_saving_directory)
                        if file_ost_path_info is None:
                            time.sleep(0.1)
                            continue
                        else:
                            ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = file_ost_path_info
                        # print(ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number)
                        file_mdt_path_info = remote_statistics_collector.collect_file_mdt_path_info(
                            self.pid,
                            self.server_saving_directory)
                        if file_mdt_path_info is None:
                            continue
                        else:
                            mdt_kernel_path, mdt_dir_name = file_mdt_path_info
                        # print(mdt_kernel_path, mdt_dir_name)
                        ost_value_list, ost_stats_so_far = remote_statistics_collector.process_ost_stat(ost_kernel_path,
                                                                                                        ost_dir_name,
                                                                                                        ost_stats_so_far)
                        # print (ost_value_list, ost_stats_so_far)
                        # mdt_value_list, all_mdt_stat_so_far_dict = get_mdt_stat(remote_global_vars.mdt_parent_path, mdt_paths,
                        #                                                         all_mdt_stat_so_far_dict)
                        mdt_value_list, mdt_stat_so_far_general = remote_statistics_collector.get_mdt_stat(
                            self.mdt_parent_path,
                            mdt_dir_name,
                            mdt_stat_so_far_general)
                        # print (mdt_value_list, mdt_stat_so_far_general)
                        ost_agent_address = self.remote_ost_index_to_ost_agent_address_dict.get(ost_number) or ""
                        remote_ost_value_list = [0.0, 0.0]
                        if ost_agent_address != "":
                            remote_ost_stats_so_far = all_remote_ost_stats_so_far.get(remote_ost_dir_name) or {}
                            remote_ost_value_list, remote_ost_stats_so_far = remote_statistics_collector.process_lustre_ost_stats(
                                ost_agent_address, remote_ost_dir_name, remote_ost_stats_so_far)
                            all_remote_ost_stats_so_far[remote_ost_dir_name] = remote_ost_stats_so_far
                        # print (all_remote_ost_stats_so_far)
                        output_string = str(time.time()) + ","
                        output_string += network_statistics_collector.get_log_str()

                        for item in system_value_list:
                            output_string += "," + str(item)
                        for item in buffer_value_list:
                            output_string += "," + str(item)
                        # ost_value_list are metrics with index 79-95 in csv
                        for item in ost_value_list:
                            output_string += "," + str(item)
                        # values with index 112-147
                        for item in mdt_value_list:
                            output_string += "," + str(item)

                        output_string += "," + str(network_statistics_collector.dsack_dups)
                        output_string += "," + str(network_statistics_collector.reord_seen)

                        output_string += "," + str(system_monitoring_global_vars.system_cpu_usage)
                        output_string += "," + str(system_monitoring_global_vars.system_memory_usage)

                        for item in remote_ost_value_list:
                            output_string += "," + str(item)

                        # mdt_value_list : total_mdt_numbers at 100
                        # repeat "total_mdt_numbers" of times in list
                        # string of mdt name to use as key for map, foK36 metrics for each mdt
                        # for item in mdt_value_list:
                        #     output_string += "," + str(item)

                        output_string += "," + str(self.label_value) + "\n"
                        epoc_count += 1
                        if Config.send_to_cloud_mode and not is_first_time:
                            epoc_time += 1
                            data = {}
                            metrics_data = data_converter.data_str_to_json(output_string)
                            data["transfer_ID"] = transfer_id
                            data["data"] = metrics_data
                            data["sequence_number"] = epoc_time
                            data["is_sender"] = 0
                            body = json.dumps(data)
                            # print(body)
                            # data_transfer_overhead = len(body.encode('utf-8'))
                            metric_publisher_socket.send_json(body)
                        elif not is_first_time:
                            main_output_string += output_string
                            if epoc_count % 5 == 0:
                                print("transferring file.... ", epoc_count, "label: ", self.label_value)
                                if epoc_count % 100 == 0:
                                    print("transferring file.... ", epoc_count, "label: ", self.label_value)
                                    epoc_count = 0
                                write_thread = fileWriteThread(main_output_string, "./receiver/logs/dataset_",
                                                               self.label_value)
                                write_thread.start()
                                main_output_string = ""
                        else:
                            print("skip first transfer")
                            is_first_time = False
                except psutil.NoSuchProcess as e:
                    print(e.msg)
                    print("EXITNG COLLECT STAT THREAD")
                    self.is_transfer_done = True
                except:
                    traceback.print_exc()
                # processing_finish_time = time.time()
                # processing_time = processing_finish_time - processing_start_time
                # # cpu_memory_overhead = agent_resource_usage_collector.get_process_io_stats(sender_monitor_agent_pid,
                # #                                                                           sender_monitor_agent_process)
                # overhead_output_string = "{},{},{},{},{}\n".format(processing_finish_time,
                #                                                    processing_time,
                #                                                    data_transfer_overhead,
                #                                                    remote_global_vars.receiver_monitor_agent_process.cpu_percent(),
                #                                                    remote_global_vars.receiver_monitor_agent_process.memory_percent())
                # overhead_epoc_count += 1
                # if not is_first_time:
                #    overhead_main_output_string += overhead_output_string
                #    if overhead_epoc_count % 10 == 0:
                #        overhead_epoc_count = 0
                #        overhead_write = overheadFileWriteThread("./receiver/overhead_logs/overhead_footprints.csv", overhead_main_output_string)
                #        overhead_write.start()
                #       overhead_main_output_string = ""

                time.sleep(sleep_time)
