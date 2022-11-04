from multiprocessing import Value, Array, Manager
manager = Manager()
global_dict = manager.dict()
pid = Value('i', -1)
# label_value = None
global_dict['label_value'] = None
sender_process_pid = Value('i', -1)
global_dict['sender_process'] = None
server_process_pid = Value('i', -1)
global_dict['server_process'] = None
ready_to_publish = Value('b', False)
# mdt_parent_path = Value('c', "")
global_dict['mdt_parent_path'] = ""
should_run = Value('b', True)
monitor_agent_pid = Value('i', -1)
# monitor_agent_process = None
global_dict['monitor_agent_process'] = None
should_run.value = False

system_memory_usage = Value('d', -1)
system_cpu_usage = Value('d', -1)
system_cpu_mem_usage = Array('d', [-1, -1])
system_lustre_nic_io_dict = manager.dict({"nic_send_bytes": 0.0, "nic_receive_bytes": 0.0})
# system_cpu_mem_usage = manager.list(range(2))

# system_cpu_mem_usage_dict = {"system_cpu_percent": -1, "system_memory_percent": -1}
system_cpu_mem_usage_dict = manager.dict({"system_cpu_percent": -1, "system_memory_percent": -1})
# system_cpu_mem_usage_proto_message = ResourceUsageMetrics()
# system_cpu_mem_usage_proto_message.system_cpu_percent = -1
# system_cpu_mem_usage_proto_message.system_memory_percent = -1
#
system_buffer_value = Array('d', [0, 0, 0, 0, 0, 0])
# system_buffer_value_dict = {"tcp_rcv_buffer_min": 0, "tcp_rcv_buffer_default": 0, "tcp_rcv_buffer_max": 0, "tcp_snd_buffer_min": 0, "tcp_snd_buffer_default": 0, "tcp_snd_buffer_max": 0}
system_buffer_value_dict = manager.dict({"tcp_rcv_buffer_min": 0, "tcp_rcv_buffer_default": 0, "tcp_rcv_buffer_max": 0,
                            "tcp_snd_buffer_min": 0, "tcp_snd_buffer_default": 0, "tcp_snd_buffer_max": 0})
client_ost_metrics_dict = manager.dict({})
client_mdt_metrics_dict = manager.dict({})
client_io_metrics_dict = manager.dict({})
dtn_io_metrics_dict = manager.dict({"dtn_lustre_read_bytes": 0.0, "dtn_lustre_write_bytes": 0.0})
