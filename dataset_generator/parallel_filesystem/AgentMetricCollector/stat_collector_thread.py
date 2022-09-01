import json
import threading
import time
import traceback
import psutil
import zmq
import hashlib
from datetime import datetime
from subprocess import Popen, PIPE

from google.protobuf.json_format import MessageToDict
from collectors.network_metric_collector_ss_v2 import NetworkMetricCollectorSS_V2
from collectors.system_metric_collector import SystemMetricCollector
from collectors.file_ost_path_info import FileOstPathInfo
from collectors.file_mdt_path_info import FileMdtPathInfo
from collectors.client_ost_metric_collector import ClientOstMetricCollector
from collectors.client_mdt_metric_collector import ClientMdtMetricCollector
from collectors.lustre_ost_metric_http_collector import LustreOstMetricHttpCollector
from collectors.lustre_ost_metric_zmq_collector import LustreOstMetricZmqCollector
from collectors.protobuf_messages.log_metrics_pb2 import Metrics, MonitoringLog, PublisherPayload
from helper_threads import fileWriteThread
from Config import Config
import system_monitoring_global_vars
import global_vars

class StatThread(threading.Thread):
    def __init__(self, src_ip, src_port, dst_ip, dst_port, zmq_context,
                 xsub_backend_socket_name,
                 ost_metric_backend_socket_name,
                 remote_ost_index_to_ost_agent_http_address_dict,
                 pid_str, path,
                 mdt_parent_path, label_value, is_sender,
                 write_thread_directory, over_head_write_thread_directory):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.ost_metric_backend_socket_name = ost_metric_backend_socket_name
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

    def run(self):
        self.collect_stat()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def collect_stat(self):
        is_parallel_file_system = False
        proc = Popen(['ls', '-l', '/proc/fs/'], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        parts = res.split("\n")
        for x in parts:
            if "lustre" in x:
                is_parallel_file_system = True

        network_metrics_collector = NetworkMetricCollectorSS_V2(self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.prefix)
        system_metrics_collector = SystemMetricCollector(self.prefix)
        file_ost_path_info_extractor = FileOstPathInfo()
        file_mdt_path_info_extractor = FileMdtPathInfo()
        client_ost_metrics_collector = ClientOstMetricCollector(self.prefix)
        client_mdt_metrics_collector = ClientMdtMetricCollector(self.prefix)
        # lustre_ost_metrics_http_collector = LustreOstMetricHttpCollector(self.prefix)
        lustre_ost_metrics_zmq_collector = LustreOstMetricZmqCollector(self.context, self.ost_metric_backend_socket_name, self.prefix)
        # TO DO REMOVE THIS LINE ITS JUST A TEST
        # is_parallel_file_system = True

        # if global_vars.ready_to_publish:
        # mdt_paths = []
        # mdt_stat_so_far_general = {"req_waittime": 0.0, "req_active": 0.0, "mds_getattr": 0.0,
        #                            "mds_getattr_lock": 0.0, "mds_close": 0.0, "mds_readpage": 0.0,
        #                            "mds_connect": 0.0, "mds_get_root": 0.0, "mds_statfs": 0.0,
        #                            "mds_sync": 0.0, "mds_quotactl": 0.0, "mds_getxattr": 0.0,
        #                            "mds_hsm_state_set": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0,
        #                            "seq_query": 0.0, "fld_query": 0.0,
        #                            "md_stats": {
        #                                "close": 0.0, "create": 0.0, "enqueue": 0.0, "getattr": 0.0,
        #                                "intent_lock": 0.0,
        #                                "link": 0.0, "rename": 0.0, "setattr": 0.0, "fsync": 0.0, "read_page": 0.0,
        #                                "unlink": 0.0, "setxattr": 0.0, "getxattr": 0.0,
        #                                "intent_getattr_async": 0.0, "revalidate_lock": 0.0
        #                            }}
        # all_mdt_stat_so_far_dict = {}
        # proc = Popen(['ls', '-l', self.mdt_parent_path], universal_newlines=True, stdout=PIPE)
        # res = proc.communicate()[0]
        # res_parts = res.split("\n")
        # for line in res_parts:
        #     if len(line.strip()) > 0:
        #         if "total" not in line:
        #             parts = line.split(" ")
        #             print(parts)
        #             mdt_paths.append(parts[-1])
        #             all_mdt_stat_so_far_dict[parts[-1]] = copy.deepcopy(mdt_stat_so_far_general)
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
            metric_publisher_socket.connect("inproc://{}".format(self.xsub_backend_socket_name))
        target_process = None
        try:
            target_process = psutil.Process(int(self.pid_str))
        except psutil.NoSuchProcess as e:
            print(e.msg)
            print("Exiting Collect Stat Thread. Process not found")
            self.is_transfer_done = True
        transfer_id = None
        while 1:
            processing_start_time = time.time()
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
                    print(transfer_id)
                    # TODO
                    # Send a request to the realtime detection service to add this new transfer
                time_diff += 1
                # epoc_time += 1
                network_metrics_collector.collect_metrics()

                system_metrics_collector.collect_metrics(self.pid_str, target_process)
                if is_parallel_file_system:
                    file_ost_path_info = file_ost_path_info_extractor.get_file_ost_path_info(self.pid_str, self.file_path)
                    if file_ost_path_info is None:
                        time.sleep(0.1)
                        continue
                    else:
                        ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number = file_ost_path_info
                    # print(ost_kernel_path, ost_dir_name, remote_ost_dir_name, ost_number)
                    client_ost_metrics_collector.collect_metrics(ost_kernel_path, ost_dir_name)

                    file_mdt_path_info = file_mdt_path_info_extractor.get_file_mdt_path_info(self.pid_str, self.file_path)
                    if file_mdt_path_info is None:
                        continue
                    else:
                        mdt_kernel_path, mdt_dir_name = file_mdt_path_info
                    # print(mdt_kernel_path, mdt_dir_name)
                    client_mdt_metrics_collector.collect_metrics(self.mdt_parent_path, mdt_dir_name)

                    # ost_agent_address = self.remote_ost_index_to_ost_agent_http_address_dict.get(ost_number) or ""
                    # lustre_ost_metrics_http_collector.collect_metrics(ost_agent_address, remote_ost_dir_name)
                    lustre_ost_metrics_zmq_collector.collect_metrics(ost_number, remote_ost_dir_name, int(processing_start_time))

                epoc_count += 1
                # print(output_string)
                time_second = processing_start_time
                if Config.send_to_cloud_mode and Config.communication_type == "JSON" and not is_first_time and global_vars.ready_to_publish:
                    epoc_time += 1
                    data = {}

                    metrics_data = {"time_stamp": str(time_second)}
                    metrics_data.update(network_metrics_collector.get_metrics_dict())
                    metrics_data.update(system_metrics_collector.get_metrics_dict())
                    for key in system_monitoring_global_vars.system_buffer_value_dict.keys():
                        metrics_data["{}{}".format(self.prefix, key)] = system_monitoring_global_vars.system_buffer_value_dict[key]
                    metrics_data.update(client_ost_metrics_collector.get_metrics_dict())
                    metrics_data.update(client_mdt_metrics_collector.get_metrics_dict())
                    for key in system_monitoring_global_vars.system_cpu_mem_usage_dict.keys():
                        metrics_data["{}{}".format(self.prefix, key)] = system_monitoring_global_vars.system_cpu_mem_usage_dict[key]
                    # metrics_data.update(lustre_ost_metrics_http_collector.get_metrics_dict())
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
                elif Config.send_to_cloud_mode and Config.communication_type == "PROTO" and not is_first_time and global_vars.ready_to_publish:
                    epoc_time += 1
                    monitoring_msg = MonitoringLog()

                    metrics_msg = Metrics()
                    metrics_msg.timestamp = datetime.fromtimestamp(time_second).strftime("%H:%M:%S %m-%d-%Y")
                    metrics_msg.network_metrics.CopyFrom(network_metrics_collector.get_proto_message())
                    metrics_msg.system_metrics.CopyFrom(system_metrics_collector.get_proto_message())
                    metrics_msg.buffer_value_metrics.MergeFrom(system_monitoring_global_vars.system_buffer_value_proto_message)
                    metrics_msg.client_ost_metrics.CopyFrom(client_ost_metrics_collector.get_proto_message())
                    metrics_msg.client_mdt_metrics.CopyFrom(client_mdt_metrics_collector.get_proto_message())
                    metrics_msg.resource_usage_metrics.MergeFrom(system_monitoring_global_vars.system_cpu_mem_usage_proto_message)
                    # metrics_msg.lustre_ost_metrics.CopyFrom(lustre_ost_metrics_http_collector.get_proto_message())
                    metrics_msg.lustre_ost_metrics.CopyFrom(lustre_ost_metrics_zmq_collector.get_proto_message())
                    metrics_msg.label_value = int(self.label_value)

                    monitoring_msg.metrics.CopyFrom(metrics_msg)
                    monitoring_msg.transfer_ID = transfer_id
                    monitoring_msg.sequence_number = epoc_time
                    monitoring_msg.is_sender = self.is_sender

                    log_data_request = PublisherPayload()
                    log_data_request.request_type = "send_log_data"
                    log_data_request.data.CopyFrom(monitoring_msg)
                    log_data_request.timestamp = datetime.fromtimestamp(float(processing_start_time)).strftime("%H:%M:%S.%f %m-%d-%Y")
                    metric_publisher_socket.send_json(MessageToDict(log_data_request))
                    # metric_publisher_socket.send(log_data_request.SerializeToString())
                elif not is_first_time:
                    output_string = str(time_second)
                    for item in network_metrics_collector.get_metrics_list():
                        output_string += "," + str(item)
                    for item in system_metrics_collector.get_metrics_list():
                        output_string += "," + str(item)
                    for item in system_monitoring_global_vars.system_buffer_value:
                        output_string += "," + str(item)
                    # ost_value_list are metrics with index 79-95 in csv
                    for item in client_ost_metrics_collector.get_metrics_list():
                        output_string += "," + str(item)
                    # # values with index 112-147
                    for item in client_mdt_metrics_collector.get_metrics_list():
                        output_string += "," + str(item)
                    for item in system_monitoring_global_vars.system_cpu_mem_usage:
                        output_string += "," + str(item)
                    # for item in lustre_ost_metrics_http_collector.get_metrics_list():
                    #     output_string += "," + str(item)
                    for item in lustre_ost_metrics_zmq_collector.get_metrics_list():
                        output_string += "," + str(item)
                    output_string += "," + str(self.label_value) + "\n"
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
            processing_finish_time = time.time()
            processing_time = processing_finish_time - processing_start_time
            # # cpu_memory_overhead = agent_resource_usage_collector.get_process_io_stats(global_vars.monitor_agent_pid,
            # #                                                                           global_vars.monitor_agent_process)
            # overhead_output_string = "{},{},{},{},{}\n".format(processing_finish_time,
            #                                                    processing_time,
            #                                                    data_transfer_overhead,
            #                                                    global_vars.monitor_agent_process.cpu_percent(),
            #                                                    global_vars.monitor_agent_process.memory_percent())
            # overhead_epoc_count += 1
            # if not is_first_time:
            #     overhead_main_output_string += overhead_output_string
            #     if overhead_epoc_count % 10 == 0:
            #         overhead_epoc_count = 0
            #         overhead_write = overheadFileWriteThread("./sender/overhead_logs/overhead_footprints.csv", overhead_main_output_string)
            #         overhead_write = overheadFileWriteThread("./receiver/overhead_logs/overhead_footprints.csv",overhead_main_output_string)
            #         overhead_write = overheadFileWriteThread(self.over_head_write_thread_directory,overhead_main_output_string)
            #         overhead_write.start()
            #         overhead_main_output_string = ""
            time.sleep(min(sleep_time, abs(sleep_time - processing_time)))
