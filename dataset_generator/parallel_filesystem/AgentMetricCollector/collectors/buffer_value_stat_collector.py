from subprocess import Popen, PIPE

try:
    from abstract_collector import AbstractCollector
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector


class BufferValueStatCollector(AbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {89: 'string', 90: 'string', 91: 'string', 92: 'string', 93: 'string', 94: 'string'}
        self.metrics_id_to_attr = {89: 'tcp_rcv_buffer_min', 90: 'tcp_rcv_buffer_default', 91: 'tcp_rcv_buffer_max',
                                   92: 'tcp_snd_buffer_min', 93: 'tcp_snd_buffer_default', 94: 'tcp_snd_buffer_max'}

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