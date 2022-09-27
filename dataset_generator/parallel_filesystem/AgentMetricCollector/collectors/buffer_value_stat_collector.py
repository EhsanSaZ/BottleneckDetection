from subprocess import Popen, PIPE
from google.protobuf.json_format import ParseDict, MessageToDict

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import BufferValueMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import BufferValueMetrics


class BufferValueStatCollector(AbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {1: 'string', 2: 'string', 3: 'string', 4: 'string', 5: 'string', 6: 'string'}
        self.metrics_id_to_attr = {1: 'tcp_rcv_buffer_min', 2: 'tcp_rcv_buffer_default', 3: 'tcp_rcv_buffer_max',
                                   4: 'tcp_snd_buffer_min', 5: 'tcp_snd_buffer_default', 6: 'tcp_snd_buffer_max'}

    def collect_metrics(self):
        self.get_buffer_value()

    def get_buffer_value(self):
        value_list = []

        proc = Popen(['cat', '/proc/sys/net/ipv4/tcp_rmem'], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split("\t")
        for line in res_parts:
            if len(line.strip()) > 0:
                value = int(line.strip())
                value_list.append(value)

        proc = Popen(['cat', '/proc/sys/net/ipv4/tcp_wmem'], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split("\t")
        for line in res_parts:
            if len(line.strip()) > 0:
                value = int(line.strip())
                value_list.append(value)
        self.metrics_list = value_list
        # return value_list
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
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), BufferValueMetrics())
        return message
