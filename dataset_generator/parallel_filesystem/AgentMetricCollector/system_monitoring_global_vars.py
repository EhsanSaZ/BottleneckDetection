# from collectors.protobuf_messages.log_metrics_pb2 import ResourceUsageMetrics, BufferValueMetrics
# from multiprocessing import Value, Array, Manager
# manager2 = Manager()
#
# system_memory_usage = Value('d', -1)
# system_cpu_usage = Value('d', -1)
# system_cpu_mem_usage = Array('d', [-1, -1])
# # system_cpu_mem_usage = manager.list(range(2))
#
# # system_cpu_mem_usage_dict = {"system_cpu_percent": -1, "system_memory_percent": -1}
# system_cpu_mem_usage_dict = manager2.dict({"system_cpu_percent": -1, "system_memory_percent": -1})
# # system_cpu_mem_usage_proto_message = ResourceUsageMetrics()
# # system_cpu_mem_usage_proto_message.system_cpu_percent = -1
# # system_cpu_mem_usage_proto_message.system_memory_percent = -1
# #
# system_buffer_value = Array('d', [0, 0, 0, 0, 0, 0])
# # system_buffer_value_dict = {"tcp_rcv_buffer_min": 0, "tcp_rcv_buffer_default": 0, "tcp_rcv_buffer_max": 0, "tcp_snd_buffer_min": 0, "tcp_snd_buffer_default": 0, "tcp_snd_buffer_max": 0}
# system_buffer_value_dict = manager2.dict({"tcp_rcv_buffer_min": 0, "tcp_rcv_buffer_default": 0, "tcp_rcv_buffer_max": 0,
#                             "tcp_snd_buffer_min": 0, "tcp_snd_buffer_default": 0, "tcp_snd_buffer_max": 0})
#
# # system_buffer_value_proto_message = BufferValueMetrics()
# # system_buffer_value_proto_message.tcp_rcv_buffer_min = 0
# # system_buffer_value_proto_message.tcp_rcv_buffer_default = 0
# # system_buffer_value_proto_message.tcp_rcv_buffer_max = 0
# # system_buffer_value_proto_message.tcp_snd_buffer_min = 0
# # system_buffer_value_proto_message.tcp_snd_buffer_default = 0
# # system_buffer_value_proto_message.tcp_snd_buffer_max = 0