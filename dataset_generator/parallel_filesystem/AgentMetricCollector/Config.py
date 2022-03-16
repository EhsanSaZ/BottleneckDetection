class Config:

    parallel_metric_collector_src_ip = "127.0.0.1"
    parallel_metric_collector_dst_ip = "134.197.95.46"
    parallel_metric_collector_port_number = "50505"
    parallel_metric_collector_time_length = 3600
    parallel_metric_collector_drive_name = "sda"
    parallel_metric_collector_src_path = "/home/esaeedizade/dataDir/srcData/"
    parallel_metric_collector_dst_path = "/home/esaeedizade/dataDir/dstData/"
    parallel_metric_remote_ost_index_to_ost_agent_address_dict = {0: "http://10.10.1.2:1234/", 1: "http://10.10.1.3:1234/"}
    parallel_metric_mdt_parent_path = '/proc/fs/lustre/mdc/'

    send_to_cloud_mode = False