class Config:
    parallel_metric_remote_ost_index_to_ost_agent_http_address_dict = {0: "http://10.10.1.2:1234/",
                                                                       1: "http://10.10.1.3:1234/",
                                                                       2: "http://10.10.1.4:1234/",
                                                                       3: "http://10.10.1.5:1234/",
                                                                       4: "http://10.10.1.5:1235/"}

    parallel_metric_remote_ost_index_to_ost_agent_zmq_address_dict = {0: "http://10.10.1.2:1234/",
                                                                       1: "http://10.10.1.3:1234/",
                                                                       2: "http://10.10.1.4:1234/",
                                                                       3: "http://10.10.1.5:1234/",
                                                                       4: "http://10.10.1.5:1235/"}

    parallel_metric_collector_local_ip_range = ["10.10.2.1"]#["134.197.94.169", "127.0.0.1", "127.0.1.1"]
    parallel_metric_collector_local_port_range = [40000, 41000]
    parallel_metric_collector_peer_ip_range = ["10.10.2.2", "10.10.2.3", "10.10.2.4", "10.10.2.5", "10.10.2.6", "10.10.2.7", "10.10.2.8", "10.10.2.9", "10.10.2.10", "10.10.2.11"] #["134.197.94.169", "127.0.0.1", "127.0.1.1"]
    parallel_metric_collector_peer_port_range = [50000, 51000]
    parallel_metric_collector_drive_name = "sda"

    parallel_metric_collector_src_ip = "10.10.2.1"
    parallel_metric_collector_dst_ip = "10.10.2.2"  # used by the java client app
    parallel_metric_collector_port_number = "50505"  # used by the java client and server app
    parallel_metric_collector_src_path = "/home/esaeedizade/data/srcData/"  # used by the java client app
    remote_parallel_metric_collector_server_saving_directory = "/lustre/0/writeFolder/"  # used by the java server app
    parallel_metric_collector_read_lustre_mount_point = ["/lustre/"]
    parallel_metric_collector_write_lustre_mount_point = ["/lustre/"]

    parallel_metric_mdt_parent_path = '/proc/fs/lustre/mdc/'
    parallel_metric_java_sender_app_path = '/users/Ehsan/BottleneckDetection/dataset_generator/parallel_filesystem/AgentMetricCollector/collectors/JavaApplications/SimpleSender1.java'  # used by the java client app
    remote_parallel_metric_collector_java_receiver_app_path = '/users/Ehsan/BottleneckDetection/dataset_generator/parallel_filesystem/AgentMetricCollector/collectors/JavaApplications/SimpleReceiver_per_second_thr_monitor.java'  # used by the java client app

    send_to_cloud_mode = True
    communication_type = "PROTO"  # "JSON"  # PROTO
    cloud_server_address = "127.0.0.1"
    cloud_server_port = "60000"

    xpub_frontend_socket_ip_sender = "127.0.0.1"
    xpub_frontend_socket_port_sender = "60100"

    xsub_backend_socket_name = "xsub_backend"

    # rabbit publisher
    rabbit_host = "c220g1-030616.wisc.cloudlab.us"
    rabbit_port = 5672
    rabbit_log_queue_name = "transfer_monitoring_logs"
    heartbeat_queue_name = "HEARTBEAT_QUEUE"
    rabbitmq_heartbeat_interval = 60
    cluster_name = "cluster_1"

    # OST Cache server configuration
    cache_size = 100
    cache_ttl = 15
    ost_rep_backend_socket_name = "ost_rep_backend"
