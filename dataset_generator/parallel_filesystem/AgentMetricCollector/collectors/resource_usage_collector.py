import psutil
from google.protobuf.json_format import ParseDict

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import ResourceUsageMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import ResourceUsageMetrics


class ResourceUsageCollector(AbstractCollector):
    def __init__(self, lustre_nic_name, prefix=""):
        super().__init__(prefix)
        self.lustre_nic_name = lustre_nic_name
        self.metrics_datatypes = {1: 'string', 2: 'string', 3: 'string', 4:'string'}
        self.metrics_id_to_attr = {1: 'system_cpu_percent', 2: 'system_memory_percent', 3:'nic_send_bytes', 4:'nic_receive_bytes'}
        self.nic_io_sofar = None
        self.is_first_time = True

    def collect_metrics(self):
        self.get_cpu_mem_nic()

    def get_cpu_mem_nic(self):
        value_list = []
        value_list.append(str(psutil.cpu_percent()))
        value_list.append(str(psutil.virtual_memory().percent))

        nic_io_latest = psutil.net_io_counters(pernic=True).get(self.lustre_nic_name) or None
        if nic_io_latest:
            if self.is_first_time:
                value_list.append('0')
                value_list.append('0')
                self.nic_io_sofar = nic_io_latest
                self.is_first_time = False
            else:
                value_list.append(str(nic_io_latest[0] - self.nic_io_sofar[0]))
                value_list.append(str(nic_io_latest[1] - self.nic_io_sofar[1]))
                self.nic_io_sofar = nic_io_latest
        else:
            value_list.append('0')
            value_list.append('0')
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
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), ResourceUsageMetrics())
        return message
