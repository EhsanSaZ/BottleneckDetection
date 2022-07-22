import json
from abc import ABC, abstractmethod


class AbstractCollector(ABC):
    def __init__(self, prefix):
        self.prefix = prefix
        self.metrics_list = []
        self.metrics_str = ""
        self.metrics_dict = {}
        self.metrics_datatypes = {}
        self.metrics_id_to_attr = {}

    def _is_number(self, string_):
        try:
            complex(string_)  # for int, long, float and complex
        except ValueError:
            return False
        return True

    def _get_mbps(self, thpt):
        if self._is_number(thpt):
            return thpt
        thpts = thpt.split("Gb")
        if len(thpts) == 2:
            return float(thpts[0]) * 1024
        thpts = thpt.split("Mb")
        if len(thpts) == 2:
            return float(thpts[0])
        thpts = thpt.split("Kb")
        if len(thpts) == 2:
            return float(thpts[0]) / 1024.
        thpts = thpt.split("b")
        if len(thpts) == 2:
            return float(thpts[0]) / (1024. * 1024.)
        thpts = thpt.split("MB")
        if len(thpts) == 2:
            return float(thpts[0]) * 8
        thpts = thpt.split("KB")
        if len(thpts) == 2:
            return float(thpts[0]) * 8 / 1024.
        thpts = thpt.split("B")
        if len(thpts) == 2:
            return float(thpts[0]) * 8 / 1024. * 1024.
        try:
            return float(thpt)
        except:
            return 0.0

    def _get_data_type(self, val, type_):
        if type_ == "string":
            return str(self._get_mbps(val))
        elif type_ == "float":
            return float(val)
        elif type_ == "intonly":
            tmp_value = str(val).split(".")[0]
            return str(tmp_value)
        elif type_ == "dict":
            pass
        else:
            return int(float(val))

    @abstractmethod
    def collect_metrics(self, *args):
        pass

    @abstractmethod
    def get_proto_message(self):
        pass

    def get_metrics_name_list(self):
        return list(self.metrics_id_to_attr.values())

    def get_metrics_str(self):
        return self.metrics_str

    def get_metrics_list(self):
        return self.metrics_list

    def get_metrics_dict(self):
        return self.metrics_dict

    def get_metrics_json_str(self):
        return json.dumps(self.get_metrics_dict())
