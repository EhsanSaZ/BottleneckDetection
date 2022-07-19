import psutil

try:
    from abstract_collector import AbstractCollector
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector


class ResourceUsageCollector(AbstractCollector):
    def __init__(self, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {150: 'string', 151: 'string'}
        self.metrics_id_to_attr = {150: 'system_cpu_percent', 151: 'system_memory_percent'}

    def collect_metrics(self):
        self.get_cpu_mem()

    def get_cpu_mem(self):
        value_list = []
        value_list.append(str(psutil.cpu_percent()))
        value_list.append(str(psutil.virtual_memory().percent))
        self.metrics_list = value_list
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
