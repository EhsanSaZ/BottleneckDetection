import threading

import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime
from datetime import timezone
# host = 'http://c220g1-030601.wisc.cloudlab.us:15672/'
host = 'http://3.145.181.211:15672/'
# host =  'http://0.0.0.0:15672'
queue_name = 'node1.lustrecluster.anomaly-pg0.wisc.cloudlab.us_at_cluster_1'
monitoring_period = 99999
monitoring_cycle = 1

t_second = 0
output_string = ""
epoc_count = 0

class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, file_path_prefix):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.file_path_prefix = file_path_prefix

    def run(self):
        output_file = open("{}.csv".format(self.file_path_prefix), "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


try:
    while True:
        if t_second >= monitoring_period:
            break
        response = requests.get(host + 'api/queues/%2F/' + queue_name, auth=HTTPBasicAuth('guest', 'guest')).json()
        # response = {'consumer_details': [{'arguments': {}, 'channel_details': {'connection_name': '172.20.0.10:46544 -> 172.20.0.2:5672', 'name': '172.20.0.10:46544 -> 172.20.0.2:5672 (1)', 'node': 'rabbit@559003651ecd', 'number': 1, 'peer_host': '172.20.0.10', 'peer_port': 46544, 'user': 'guest'}, 'ack_required': True, 'active': True, 'activity_status': 'up', 'consumer_tag': 'amq.ctag-q7QLyH05V7p5PPj6R4FPFw', 'exclusive': False, 'prefetch_count': 256, 'queue': {'name': 'node1.lustrecluster.anomaly-pg0.wisc.cloudlab.us_at_cluster_1', 'vhost': '/'}}], 'arguments': {}, 'auto_delete': False, 'backing_queue_status': {'avg_ack_egress_rate': 0.00012754337848573587, 'avg_ack_ingress_rate': 0.00012731096888828758, 'avg_egress_rate': 0.00012731096888828758, 'avg_ingress_rate': 2.3155807508792767e-08, 'delta': ['delta', 'undefined', 0, 0, 'undefined'], 'len': 0, 'mode': 'default', 'next_deliver_seq_id': 322333083, 'next_seq_id': 322333083, 'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'target_ram_count': 'infinity', 'version': 1}, 'consumer_capacity': 1.0, 'consumer_utilisation': 1.0, 'consumers': 1, 'deliveries': [], 'durable': False, 'effective_policy_definition': {}, 'exclusive': False, 'exclusive_consumer_tag': None, 'garbage_collection': {'fullsweep_after': 65535, 'max_heap_size': 0, 'min_bin_vheap_size': 46422, 'min_heap_size': 233, 'minor_gcs': 11}, 'head_message_timestamp': None, 'idle_since': '2022-09-28T20:50:07.080+00:00', 'incoming': [], 'memory': 12936, 'message_bytes': 0, 'message_bytes_paged_out': 0, 'message_bytes_persistent': 0, 'message_bytes_ram': 0, 'message_bytes_ready': 0, 'message_bytes_unacknowledged': 0, 'message_stats': {'ack': 322282642, 'ack_details': {'rate': 0.0}, 'deliver': 322331033, 'deliver_details': {'rate': 0.0}, 'deliver_get': 322331033, 'deliver_get_details': {'rate': 0.0}, 'deliver_no_ack': 0, 'deliver_no_ack_details': {'rate': 0.0}, 'get': 0, 'get_details': {'rate': 0.0}, 'get_empty': 0, 'get_empty_details': {'rate': 0.0}, 'get_no_ack': 0, 'get_no_ack_details': {'rate': 0.0}, 'publish': 322323589, 'publish_details': {'rate': 0.0}, 'redeliver': 47785, 'redeliver_details': {'rate': 0.0}}, 'messages': 0, 'messages_details': {'rate': 0.0}, 'messages_paged_out': 0, 'messages_persistent': 0, 'messages_ram': 0, 'messages_ready': 0, 'messages_ready_details': {'rate': 0.0}, 'messages_ready_ram': 0, 'messages_unacknowledged': 0, 'messages_unacknowledged_details': {'rate': 0.0}, 'messages_unacknowledged_ram': 0, 'name': 'node1.lustrecluster.anomaly-pg0.wisc.cloudlab.us_at_cluster_1', 'node': 'rabbit@559003651ecd', 'operator_policy': None, 'policy': None, 'recoverable_slaves': None, 'reductions': 202167976414, 'reductions_details': {'rate': 0.0}, 'single_active_consumer_tag': None, 'state': 'running', 'type': 'classic', 'vhost': '/'}
        time_stamp = datetime.now().isoformat(sep='T', timespec='milliseconds')
        message_ready_count = response["messages_ready"]
        output_string += "{},{}\n".format(time_stamp, message_ready_count)
        if epoc_count % 10 == 0:
            write_thread = fileWriteThread(output_string, "rabbitmq_monitor_result_{}".format(queue_name))
            write_thread.start()
            output_string = ""

        t_second += monitoring_cycle
        time.sleep(monitoring_cycle)
except Exception as e:
    print(e)
