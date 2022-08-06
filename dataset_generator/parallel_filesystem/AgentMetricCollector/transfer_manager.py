from stat_collector_thread import StatThread
# from receiver_stat_collector_thread import ReceiverStatThread


class TransferManager:
    def __init__(self, zmq_context, xsub_backend_socket_name, ost_rep_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                 read_path_list, write_path_list, mdt_parent_path, label_value):
        self.transfer_monitoring_threads_dict = {}
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.ost_rep_backend_socket_name = ost_rep_backend_socket_name
        self.remote_ost_index_to_ost_agent_address_dict = remote_ost_index_to_ost_agent_address_dict
        self.read_lustre_mnt_point_list = read_path_list
        self.write_lustre_mnt_point_list = write_path_list
        self.mdt_parent_path = mdt_parent_path
        self.label_value = label_value

    def add_new_monitoring_thread(self, transfer_info, is_sender, dataset_path, overhead_log_path):
        # print(transfer_info)
        pid = transfer_info["pid"]
        source_ip = transfer_info["local_ip"]
        source_port = transfer_info["local_port"]
        destination_ip = transfer_info["peer_ip"]
        destination_port = transfer_info["peer_port"]
        if is_sender:
            lustre_mnt_point_list = self.read_lustre_mnt_point_list
        else:
            lustre_mnt_point_list = self.write_lustre_mnt_point_list
        thread = StatThread(source_ip, source_port, destination_ip, destination_port,
                            self.context, self.xsub_backend_socket_name, self.ost_rep_backend_socket_name,
                            self.remote_ost_index_to_ost_agent_address_dict, str(pid),
                            lustre_mnt_point_list, self.mdt_parent_path, self.label_value,
                            is_sender, dataset_path, overhead_log_path)
        self.transfer_monitoring_threads_dict[pid] = thread
        thread.start()

    def stop_monitoring_thread(self, transfer_info):
        # print(transfer_info)
        try:
            pid = transfer_info["pid"]
            thread = self.transfer_monitoring_threads_dict.get(pid)
            if thread:
                thread.stop()
                del self.transfer_monitoring_threads_dict[pid]
        except Exception as e:
            print(e)
