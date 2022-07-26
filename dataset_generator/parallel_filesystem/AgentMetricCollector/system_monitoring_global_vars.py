from collectors.protobuf_messages.log_metrics_pb2 import ResourceUsageMetrics, BufferValueMetrics

system_memory_usage = -1
system_cpu_usage = -1
system_cpu_mem_usage = [-1, -1]
system_cpu_mem_usage_dict = {"system_cpu_percent": -1, "system_memory_percent": -1}
system_cpu_mem_usage_proto_message = ResourceUsageMetrics()
system_cpu_mem_usage_proto_message.system_cpu_percent = -1
system_cpu_mem_usage_proto_message.system_memory_percent = -1

system_buffer_value = [0, 0, 0, 0, 0, 0]
system_buffer_value_dict = {"tcp_rcv_buffer_min": 0, "tcp_rcv_buffer_default": 0, "tcp_rcv_buffer_max": 0,
                            "tcp_snd_buffer_min": 0, "tcp_snd_buffer_default": 0, "tcp_snd_buffer_max": 0}
system_buffer_value_proto_message = BufferValueMetrics()
system_buffer_value_proto_message.tcp_rcv_buffer_min = 0
system_buffer_value_proto_message.tcp_rcv_buffer_default = 0
system_buffer_value_proto_message.tcp_rcv_buffer_max = 0
system_buffer_value_proto_message.tcp_snd_buffer_min = 0
system_buffer_value_proto_message.tcp_snd_buffer_default = 0
system_buffer_value_proto_message.tcp_snd_buffer_max = 0
