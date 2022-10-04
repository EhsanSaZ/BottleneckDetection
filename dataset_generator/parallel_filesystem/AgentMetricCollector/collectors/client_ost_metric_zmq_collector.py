from subprocess import Popen, PIPE
from google.protobuf.json_format import ParseDict
import traceback
import zmq
from zmq import ZMQError


try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import ClientOstMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import ClientOstMetrics


class ClientOstMetricZmqCollector(AbstractCollector):
    def __init__(self, zmq_context, backend_socket_name, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {1: 'string', 2: 'string', 3: 'string', 4: 'string', 5: 'string', 6: 'string',
                                  7: 'string', 8: 'string', 9: 'string', 10: 'string', 11: 'string', 12: 'string',
                                  13: 'string', 14: 'string', 15: 'string', 16: 'string', 17: 'string'}
        self.metrics_id_to_attr = {1: 'req_waittime', 2: 'req_active', 3: 'read_bytes', 4: 'write_bytes',
                                   5: 'ost_setattr', 6: 'ost_read', 7: 'ost_write', 8: 'ost_get_info', 9: 'ost_connect',
                                   10: 'ost_punch', 11: 'ost_statfs', 12: 'ost_sync', 13: 'ost_quotactl',
                                   14: 'ldlm_cancel', 15: 'obd_ping', 16: 'pending_read_pages',
                                   17: 'read_RPCs_in_flight'}
        self.ost_stats_so_far = {"req_waittime": 0.0, "req_active": 0.0, "read_bytes": 0.0, "write_bytes": 0.0,
                                 "ost_setattr": 0.0, "ost_read": 0.0, "ost_write": 0.0, "ost_get_info": 0.0,
                                 "ost_connect": 0.0, "ost_punch": 0.0, "ost_statfs": 0.0, "ost_sync": 0.0,
                                 "ost_quotactl": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0}
        self.seperator_string = '--result--'
        self.latest_ost_number = ''
        self.backend_socket_name = backend_socket_name
        self.context = zmq_context
        self.socket = None
        self.initialize_socket()

    def initialize_socket(self):
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("ipc://{}".format(self.backend_socket_name))

    def reset_socket(self):
        self.socket.close()
        self.initialize_socket()

    def collect_metrics(self, ost_dir_name, time_stamp):
        self.process_ost_stat(ost_dir_name, time_stamp, self.ost_stats_so_far)

    def process_ost_stat(self, ost_dir_name, time_stamp, ost_stat_so_far):
        try:

            body = {"ost_dir_name": ost_dir_name, "time_stamp": time_stamp}
            self.socket.send_json(body)
            response = self.socket.recv_json()
            if response["status"] == "success":
                stat_response = response["stats"]
                rpc_stats_response = response["rpc_stats"]
                value_list = []

                ost_stats_parts = stat_response.split("\n")
                ost_stat_latest_values = {}
                for metric_line in ost_stats_parts:
                    if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line and get_param_arg_stats not in metric_line:
                        tokens = str(metric_line).split(" ")
                        ost_stat_latest_values[tokens[0]] = float(tokens[len(tokens) - 2])
                value_list.append(float((ost_stat_latest_values.get("req_waittime") or 0) - (ost_stat_so_far.get("req_waittime") or 0)))
                value_list.append(float((ost_stat_latest_values.get("req_active") or 0) - (ost_stat_so_far.get("req_active") or 0)))
                value_list.append(float((ost_stat_latest_values.get("read_bytes") or 0) - (ost_stat_so_far.get("read_bytes") or 0)))
                value_list.append(float((ost_stat_latest_values.get("write_bytes") or 0) - (ost_stat_so_far.get("write_bytes") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_setattr") or 0) - (ost_stat_so_far.get("ost_setattr") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_read") or 0) - (ost_stat_so_far.get("ost_read") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_write") or 0) - (ost_stat_so_far.get("ost_write") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_get_info") or 0) - (ost_stat_so_far.get("ost_get_info") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_connect") or 0) - (ost_stat_so_far.get("ost_connect") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_punch") or 0) - (ost_stat_so_far.get("ost_punch") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_statfs") or 0) - (ost_stat_so_far.get("ost_statfs") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_sync") or 0) - (ost_stat_so_far.get("ost_sync") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ost_quotactl") or 0) - (ost_stat_so_far.get("ost_quotactl") or 0)))
                value_list.append(float((ost_stat_latest_values.get("ldlm_cancel") or 0) - (ost_stat_so_far.get("ldlm_cancel") or 0)))
                value_list.append(float((ost_stat_latest_values.get("obd_ping") or 0) - (ost_stat_so_far.get("obd_ping") or 0)))

                rpc_stats_part = rpc_stats_response.split("\n")
                for metric_line in rpc_stats_part:
                    if "pending read pages" in metric_line:
                        index = metric_line.find(":")
                        value = float(metric_line[index + 1:])
                        value_list.append(value)

                    if "read RPCs in flight" in metric_line:
                        index = metric_line.find(":")
                        value = float(metric_line[index + 1:])
                        value_list.append(value)

                self.ost_stats_so_far = ost_stat_latest_values
            else:
                value_list = []
                for i in range(len(self.metrics_id_to_attr)):
                    value_list.append(0.0)

            self.metrics_list = value_list
            self.metrics_list_to_str()
            self.metrics_list_to_dict()

        except ZMQError as e:
            self.latest_ost_number = -1
            self.reset_socket()
        except Exception as e:
            traceback.print_exc()

    def metrics_list_to_str(self):
        output_string = ""
        keys_list = list(self.metrics_id_to_attr.keys())
        for index in range(len(self.metrics_list)):
            type_ = self.metrics_datatypes[keys_list[index]]
            output_string += "," + str(self._get_data_type(self.metrics_list[index], type_))
        # for item in self.metrics_list:
        #     output_string += "," + str(item)
        if output_string.startswith(","):
            output_string = output_string[1:]
        self.metrics_str = output_string

    def metrics_list_to_dict(self):
        tmp_dict = {}
        keys_list = list(self.metrics_id_to_attr.keys())
        for index in range(len(self.metrics_list)):
            type_ = self.metrics_datatypes[keys_list[index]]
            tmp_dict["{}{}".format(self.prefix, self.metrics_id_to_attr[keys_list[index]])] = self._get_data_type(
                self.metrics_list[index], type_)
        self.metrics_dict = tmp_dict

    def get_metrics_list_to_dict_no_prefix(self):
        metrics_dict_no_prefix = {}
        keys_list = list(self.metrics_id_to_attr.keys())
        for index in range(len(self.metrics_list)):
            type_ = self.metrics_datatypes[keys_list[index]]
            metrics_dict_no_prefix[self.metrics_id_to_attr[keys_list[index]]] = self._get_data_type(
                self.metrics_list[index], type_)
        return metrics_dict_no_prefix

    def get_proto_message(self):
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), ClientOstMetrics())
        return message
