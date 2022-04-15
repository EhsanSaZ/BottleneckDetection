class Config:

    parallel_metric_collector_src_ip = "10.10.2.1"
    parallel_metric_collector_dst_ip = "10.10.2.2"
    parallel_metric_collector_port_number = "50505"
    parallel_metric_collector_time_length = 3600
    parallel_metric_collector_drive_name = "sda"
    parallel_metric_collector_src_path = "/lustre/dataDir/srcData/"
    parallel_metric_collector_dst_path = "/lustre/dataDir/dstData/"
    parallel_metric_remote_ost_index_to_ost_agent_address_dict = {0: "http://10.10.1.2:1234/", 1: "http://10.10.1.3:1234/"}
    parallel_metric_mdt_parent_path = '/proc/fs/lustre/mdc/'
    parallel_metric_java_sender_app_path = '../../utilities/SimpleSender1.java'
    zmq_sender_publisher_bind_addr = "*"
    zmq_sender_publisher_port = "5556"

    remote_parallel_metric_collector_server_ip = "10.10.2.2"
    remote_parallel_metric_collector_server_port_number = "50505"
    remote_parallel_metric_collector_client_ip = "10.10.2.1"
    remote_parallel_metric_collector_remote_ost_index_to_ost_agent_address_dict = {0: "http://10.10.1.2:1234/", 1: "http://10.10.1.3:1234/"}
    remote_parallel_metric_collector_time_length = 3600
    remote_parallel_metric_collector_drive_name = "sda"
    remote_parallel_metric_collector_server_saving_directory = "/lustre/receiverDataDir/dstData/"
    remote_parallel_metric_collector_mdt_parent_path = '/proc/fs/lustre/mdc/'
    remote_parallel_metric_collector_java_receiver_app_path = '/users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java'
    zmq_receiver_publisher_bind_addr = "*"
    zmq_receiver_publisher_port = "5557"

    send_to_cloud_mode = False