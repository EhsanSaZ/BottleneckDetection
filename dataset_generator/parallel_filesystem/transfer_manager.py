from sender_stat_collector_thread import SenderStatThread
from receiver_stat_collector_thread import ReceiverStatThread

class TransferManager:
    def __init__(self, zmq_context, xsub_backend_socket_name, remote_ost_index_to_ost_agent_address_dict,
                 src_path, mdt_parent_path, label_value):
        self.transfer_monitoring_threads_dict = {}
        self.context = zmq_context
        self.xsub_backend_socket_name = xsub_backend_socket_name
        self.remote_ost_index_to_ost_agent_address_dict = remote_ost_index_to_ost_agent_address_dict
        self.src_path = src_path
        self.mdt_parent_path = mdt_parent_path
        self.label_value = label_value

    def add_new_sender_monitoring_thread(self, transfer_info):
        # print(transfer_info)
        pid = transfer_info["pid"]
        source_ip = transfer_info["local_ip"]
        source_port = transfer_info["local_port"]
        destination_ip = transfer_info["peer_ip"]
        destination_port = transfer_info["peer_port"]
        thread = SenderStatThread(source_ip, source_port, destination_ip, destination_port,
                                  self.context, self.xsub_backend_socket_name,
                                  self.remote_ost_index_to_ost_agent_address_dict, str(pid),
                                  self.src_path, self.mdt_parent_path, self.label_value)
        self.transfer_monitoring_threads_dict[pid] = thread
        thread.start()

    def add_new_receiver_transfer_monitoring_thread(self, transfer_info):
        pid = transfer_info["pid"]
        source_ip = transfer_info["local_ip"]
        source_port = transfer_info["local_port"]
        destination_ip = transfer_info["peer_ip"]
        destination_port = transfer_info["peer_port"]
        thread = ReceiverStatThread(source_ip, source_port, destination_ip, destination_port,
                                    self.context, self.xsub_backend_socket_name,
                                    self.remote_ost_index_to_ost_agent_address_dict, str(pid),
                                    self.src_path, self.mdt_parent_path, self.label_value)
        self.transfer_monitoring_threads_dict[pid] = thread
        thread.start()

    def stop_monitoring_thread(self, transfer_info):
        # print(transfer_info)
        pid = transfer_info["pid"]
        thread = self.transfer_monitoring_threads_dict.get(pid)
        if thread:
            thread.stop()
            del self.transfer_monitoring_threads_dict[pid]
