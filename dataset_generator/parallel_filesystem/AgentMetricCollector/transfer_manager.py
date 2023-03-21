from stat_collector_thread import StatProcess
# from receiver_stat_collector_thread import ReceiverStatThread


class TransferManager:
    def __init__(self, zmq_context, xsub_backend_socket_name, ost_rep_backend_socket_name,
                 client_ost_metric_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                 read_path_list, write_path_list, mdt_parent_path, label_value, ready_to_publish, buffer_value_dict,
                 client_ost_metrics_dict, system_lustre_nic_io_dict):
        self.transfer_monitoring_processes_dict = {}
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.ost_rep_backend_socket_name = ost_rep_backend_socket_name
        self.client_ost_metric_backend_socket_name = client_ost_metric_backend_socket_name
        # self.client_mdt_metric_backend_socket_name = client_mdt_metric_backend_socket_name
        self.remote_ost_index_to_ost_agent_address_dict = remote_ost_index_to_ost_agent_address_dict
        self.read_lustre_mnt_point_list = read_path_list
        self.write_lustre_mnt_point_list = write_path_list
        self.mdt_parent_path = mdt_parent_path
        self.label_value = label_value
        self.ready_to_publish = ready_to_publish
        # self.cpu_mem_dict = cpu_mem_dict
        self.buffer_value_dict = buffer_value_dict
        self.client_ost_metrics_dict = client_ost_metrics_dict
        # self.client_mdt_metrics_dict = client_mdt_metrics_dict
        # self.dtn_io_metrics_dict = dtn_io_metrics_dict
        self.system_lustre_nic_io_dict = system_lustre_nic_io_dict

    def add_new_monitoring_process(self, transfer_info, is_sender, dataset_path, overhead_log_path):
        # print(transfer_info)
        # print(self.ready_to_publish.value)
        pid = transfer_info["pid"]
        source_ip = transfer_info["local_ip"]
        source_port = transfer_info["local_port"]
        destination_ip = transfer_info["peer_ip"]
        destination_port = transfer_info["peer_port"]
        # print(self.cpu_mem_dict, )
        # print(self.buffer_value_dict)
        if is_sender:
            lustre_mnt_point_list = self.read_lustre_mnt_point_list
        else:
            lustre_mnt_point_list = self.write_lustre_mnt_point_list
        process = StatProcess(source_ip, source_port, destination_ip, destination_port,
                            self.context, self.xsub_backend_socket_name, self.ost_rep_backend_socket_name,
                            self.client_ost_metric_backend_socket_name,
                            self.remote_ost_index_to_ost_agent_address_dict, str(pid),
                            lustre_mnt_point_list, self.mdt_parent_path, self.label_value,
                            is_sender, dataset_path, overhead_log_path, self.ready_to_publish,
                            self.buffer_value_dict,
                            self.client_ost_metrics_dict,
                            self.system_lustre_nic_io_dict)
        self.transfer_monitoring_processes_dict[pid] = process
        process.start()

    def stop_monitoring_process(self, transfer_info):
        # print(transfer_info)
        try:
            pid = transfer_info["pid"]
            process = self.transfer_monitoring_processes_dict.get(pid)
            if process:
                process.stop()
                process.join()
                # process.terminate()
                del self.transfer_monitoring_processes_dict[pid]
        except Exception as e:
            print(e)
