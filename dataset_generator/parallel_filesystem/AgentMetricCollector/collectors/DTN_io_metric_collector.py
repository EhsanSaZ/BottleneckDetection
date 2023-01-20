from subprocess import Popen, PIPE

from google.protobuf.json_format import ParseDict

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import DTNLustreIoMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import DTNLustreIoMetrics


class DtnIoMetricsCollector(AbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)

        self.metrics_datatypes = {1: 'string', 2: 'string'}
        self.metrics_id_to_attr = {1: 'dtn_lustre_read_bytes', 2: 'dtn_lustre_write_bytes'}
        self.dtn_io_so_far = {"dtn_lustre_read_bytes": 0.0, "dtn_lustre_write_bytes": 0.0}
        self.seperator_string = '--result--'
        self.first_time = True
    def collect_metrics(self, from_dict=None):
        self.process_client_io_stat(from_dict)

    def process_client_io_stat(self, from_dict):
        all_clients_stats = from_dict

        dtn_io_latest_value = {"dtn_lustre_read_bytes": 0.0, "dtn_lustre_write_bytes": 0.0}
        value_list = []

        for client_id in all_clients_stats.keys():
            stats_dict = all_clients_stats.get(client_id)
            client_stat_parts = stats_dict.get("stats").split("\n")
            client_io_latest_value = {}
            for metric_line in client_stat_parts:
                if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
                    tokens = str(metric_line).split(" ")
                    if tokens[0] == "read_bytes" or tokens[0] == "write_bytes":
                        client_io_latest_value[tokens[0]] = float(tokens[len(tokens) - 1])
            dtn_io_latest_value["dtn_lustre_read_bytes"] += client_io_latest_value.get("read_bytes") or 0
            dtn_io_latest_value["dtn_lustre_write_bytes"] += client_io_latest_value.get("write_bytes") or 0
            if self.first_time is True:
                self.first_time = False
        if not self.first_time:
            value_list.append(float((dtn_io_latest_value.get("dtn_lustre_read_bytes") or 0) - (self.dtn_io_so_far.get("dtn_lustre_read_bytes") or 0)))
            value_list.append(float((dtn_io_latest_value.get("dtn_lustre_write_bytes") or 0) - (self.dtn_io_so_far.get("dtn_lustre_write_bytes") or 0)))
        else:
            value_list = [0.0, 0.0]

        self.dtn_io_so_far = dtn_io_latest_value
        self.metrics_list = value_list
        self.metrics_list_to_str()
        self.metrics_list_to_dict()

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
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), DTNLustreIoMetrics())
        return message
