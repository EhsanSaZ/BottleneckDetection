import time
import traceback

from google.protobuf.json_format import ParseDict, MessageToDict
import zmq
from zmq import ZMQError

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import LustreOstMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import LustreOstMetrics


class LustreOstMetricZmqCollector(AbstractCollector):
    def __init__(self, backend_socket_name, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {1: 'string', 2: 'string'}
        self.metrics_id_to_attr = {1: 'remote_ost_read_bytes', 2: 'remote_ost_write_bytes'}
        self.all_remote_ost_stats_so_far = {}
        self.latest_ost_number = -1
        self.backend_socket_name = backend_socket_name
        self.context = zmq.Context()
        self.socket = None
        self.initialize_socket()

    def initialize_socket(self):
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("inproc://{}".format(self.backend_socket_name))

    def reset_socket(self):
        self.socket.close()
        self.initialize_socket()

    def collect_metrics(self, ost_number, remote_ost_dir_name, time_stamp):
        self.process_lustre_ost_stats(ost_number, remote_ost_dir_name, time_stamp)

    def process_lustre_ost_stats(self, ost_number, remote_ost_dir_name, time_stamp):
        try:
            if ost_number != self.latest_ost_number:
            #     self.reset_socket()
            #     self.socket.connect(ost_agent_address)
                self.latest_ost_number = ost_number
            # path = "obdfilter." + remote_ost_dir_name + ".stats"
            body = {"ost_dir_name": remote_ost_dir_name, "time_stamp": time_stamp,
                    "ost_number": ost_number}
            self.socket.send_json(body)
            response = self.socket.recv_json()
            # print(r.json()["out_put"])
            output = response["out_put"] or ""
            if output != "":
                value_list = []
                remote_ost_stats_so_far = self.all_remote_ost_stats_so_far.get(remote_ost_dir_name) or {}
                output_parts = output.split("\n")
                remote_ost_stats_latest_value = {}
                for metric_line in output_parts:
                    if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line and not remote_ost_dir_name in metric_line:
                        tokens = str(metric_line).split(" ")
                        if tokens[0] == "read_bytes" or tokens[0] == "write_bytes":
                            remote_ost_stats_latest_value[tokens[0]] = float(tokens[len(tokens) - 1])

                value_list.append(float((remote_ost_stats_latest_value.get("read_bytes") or 0) - (
                            remote_ost_stats_so_far.get("read_bytes") or 0)))
                value_list.append(float((remote_ost_stats_latest_value.get("write_bytes") or 0) - (
                            remote_ost_stats_so_far.get("write_bytes") or 0)))
                # return value_list, remote_ost_stats_latest_value
            else:
                value_list = [0.0, 0.0]
                remote_ost_stats_latest_value = {"read_bytes": 0.0, "write_bytes": 0.0}
            self.metrics_list = value_list
            self.all_remote_ost_stats_so_far[remote_ost_dir_name] = remote_ost_stats_latest_value
            self.metrics_list_to_str()
            self.metrics_list_to_dict()
        except ZMQError as e:
            self.latest_ost_number = -1
            self.reset_socket()
        except Exception as e:
            traceback.print_exc()
        # return value_list, remote_ost_stats_latest_value

    def metrics_list_to_str(self):
        output_string = ""
        for item in self.metrics_list:
            output_string += "," + str(item)
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
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), LustreOstMetrics())
        return message
