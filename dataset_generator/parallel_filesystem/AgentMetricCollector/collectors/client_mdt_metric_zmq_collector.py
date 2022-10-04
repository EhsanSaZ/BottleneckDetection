from subprocess import Popen, PIPE

from google.protobuf.json_format import ParseDict
import traceback
import zmq
from zmq import ZMQError

try:
    from abstract_collector import AbstractCollector
    from protobuf_messages.log_metrics_pb2 import ClientMdtMetrics
except ModuleNotFoundError:
    from .abstract_collector import AbstractCollector
    from .protobuf_messages.log_metrics_pb2 import ClientMdtMetrics


class ClientMdtMetricZmqCollector(AbstractCollector):
    def __init__(self, zmq_context, backend_socket_name, prefix=""):
        super().__init__(prefix)
        self.metrics_datatypes = {112: 'string', 113: 'string', 114: 'string', 115: 'string', 116: 'string',
                                  117: 'string', 118: 'string', 119: 'string', 120: 'string', 121: 'string',
                                  122: 'string', 123: 'string', 124: 'string', 125: 'string', 126: 'string',
                                  127: 'string', 128: 'string', 129: 'string', 130: 'string', 131: 'string',
                                  132: 'string', 133: 'string', 134: 'string', 135: 'string', 136: 'string',
                                  137: 'string', 138: 'string', 139: 'string', 140: 'string', 141: 'string',
                                  142: 'string', 143: 'string', 144: 'string', 145: 'string', 146: 'string',
                                  147: 'string'}
        self.metrics_id_to_attr = {112: 'avg_waittime_md', 113: 'inflight_md', 114: 'unregistering_md',
                                   115: 'timeouts_md', 116: 'req_waittime_md', 117: 'req_active_md',
                                   118: 'mds_getattr_md', 119: 'mds_getattr_lock_md', 120: 'mds_close_md',
                                   121: 'mds_readpage_md', 122: 'mds_connect_md', 123: 'mds_get_root_md',
                                   124: 'mds_statfs_md', 125: 'mds_sync_md', 126: 'mds_quotactl_md',
                                   127: 'mds_getxattr_md', 128: 'mds_hsm_state_set_md', 129: 'ldlm_cancel_md',
                                   130: 'obd_ping_md', 131: 'seq_query_md', 132: 'fld_query_md', 133: 'close_md',
                                   134: 'create_md', 135: 'enqueue_md', 136: 'getattr_md', 137: 'intent_lock_md',
                                   138: 'link_md', 139: 'rename_md', 140: 'setattr_md', 141: 'fsync_md',
                                   142: 'read_page_md', 143: 'unlink_md', 144: 'setxattr_md', 145: 'getxattr_md',
                                   146: 'intent_getattr_async_md', 147: 'revalidate_lock_md'}
        self.mdt_stat_so_far = {"req_waittime": 0.0, "req_active": 0.0, "mds_getattr": 0.0,
                                "mds_getattr_lock": 0.0, "mds_close": 0.0, "mds_readpage": 0.0,
                                "mds_connect": 0.0, "mds_get_root": 0.0, "mds_statfs": 0.0,
                                "mds_sync": 0.0, "mds_quotactl": 0.0, "mds_getxattr": 0.0,
                                "mds_hsm_state_set": 0.0, "ldlm_cancel": 0.0, "obd_ping": 0.0,
                                "seq_query": 0.0, "fld_query": 0.0,
                                "md_stats": {
                                    "close": 0.0, "create": 0.0, "enqueue": 0.0, "getattr": 0.0,
                                    "intent_lock": 0.0,
                                    "link": 0.0, "rename": 0.0, "setattr": 0.0, "fsync": 0.0, "read_page": 0.0,
                                    "unlink": 0.0, "setxattr": 0.0, "getxattr": 0.0,
                                    "intent_getattr_async": 0.0, "revalidate_lock": 0.0
                                }}
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

    def collect_metrics(self, mdt_dir_name, time_stamp):
        self.get_mdt_stat(mdt_dir_name, time_stamp, self.mdt_stat_so_far)

    def get_mdt_stat(self, mdt_dir_name, time_stamp, mdt_stat_so_far_dict):
        try:
            body = {"mdt_dir_name": mdt_dir_name, "time_stamp": time_stamp}
            self.socket.send_json(body)
            response = self.socket.recv_json()
            if response["status"] == "success":
                import_response = response["import"]
                stat_response = response["stats"]
                md_stats_response = response["md_stats"]
                value_list = []
                value_list += self.process_mds_rpc(import_response)
                a_list, mdt_stat_latest_values = self.process_mdt_stat(mdt_stat_so_far_dict, stat_response, md_stats_response)
                value_list += a_list
                self.mdt_stat_so_far = mdt_stat_latest_values
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

    def process_mds_rpc(self, import_output):
        res_parts = import_output.split("\n")
        res_parts = import_output.split("\n")
        value_list = []
        value_dict = {}
        for metric_line in res_parts:
            if "avg_waittime:" in metric_line:
                s_index = metric_line.find(":")
                e_index = metric_line.find("usec")
                avg_waittime = float(metric_line[s_index + 1:e_index].strip())
                value_dict["avg_waittime"] = avg_waittime
                # value_list.append(avg_waittime)

            if "inflight:" in metric_line:
                s_index = metric_line.find(":")
                inflight = float(metric_line[s_index + 1:].strip())
                value_dict["inflight"] = inflight
                # value_list.append(inflight)

            if "unregistering:" in metric_line:
                s_index = metric_line.find(":")
                unregistering = float(metric_line[s_index + 1:].strip())
                value_dict["unregistering"] = unregistering
                # value_list.append(unregistering)

            if "timeouts:" in metric_line:
                s_index = metric_line.find(":")
                timeouts = float(metric_line[s_index + 1:].strip())
                value_dict["timeouts"] = timeouts
                # value_list.append(timeouts)
        value_list.append(value_dict.get('avg_waittime') or 0.0)
        value_list.append(value_dict.get('inflight') or 0.0)
        value_list.append(value_dict.get('unregistering') or 0.0)
        value_list.append(value_dict.get('timeouts') or 0.0)
        return value_list

    def process_mdt_stat(self, mdt_stat_so_far, stats_output, md_stats_output):
        value_list = []
        res_parts = stats_output.split("\n")
        mdt_stat_latest_values = {}
        for metric_line in res_parts:
            if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
                tokens = str(metric_line).split(" ")
                mdt_stat_latest_values[tokens[0]] = float(tokens[len(tokens) - 2])
                # value_list.append(tokens[0])
                # value = float(tokens[len(tokens) - 2])
                # value_list.append(value)
        value_list.append(float((mdt_stat_latest_values.get("req_waittime") or 0) - (mdt_stat_so_far.get("req_waittime") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("req_active") or 0) - (mdt_stat_so_far.get("req_active") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_getattr") or 0) - (mdt_stat_so_far.get("mds_getattr") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_getattr_lock") or 0) - (mdt_stat_so_far.get("mds_getattr_lock") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_close") or 0) - (mdt_stat_so_far.get("mds_close") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_readpage") or 0) - (mdt_stat_so_far.get("mds_readpage") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_connect") or 0) - (mdt_stat_so_far.get("mds_connect") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_get_root") or 0) - (mdt_stat_so_far.get("mds_get_root") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_statfs") or 0) - (mdt_stat_so_far.get("mds_statfs") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_sync") or 0) - (mdt_stat_so_far.get("mds_sync") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_quotactl") or 0) - (mdt_stat_so_far.get("mds_quotactl") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_getxattr") or 0) - (mdt_stat_so_far.get("mds_getxattr") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("mds_hsm_state_set") or 0) - (mdt_stat_so_far.get("mds_hsm_state_set") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("ldlm_cancel") or 0) - (mdt_stat_so_far.get("ldlm_cancel") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("obd_ping") or 0) - (mdt_stat_so_far.get("obd_ping") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("seq_query") or 0) - (mdt_stat_so_far.get("seq_query") or 0)))
        value_list.append(float((mdt_stat_latest_values.get("fld_query") or 0) - (mdt_stat_so_far.get("fld_query") or 0)))
        # proc = Popen(['lctl', 'get_param', get_param_arg], universal_newlines=True, stdout=PIPE)
        # res = proc.communicate()[0]
        res_parts = md_stats_output.split("\n")
        md_stats_so_far_dict = mdt_stat_so_far.get("md_stats") or None
        if md_stats_so_far_dict is None:
            md_stats_so_far_dict = {}
        md_stats_latest_values = {}
        # snapshot_time             1638394657.160408 secs.usecs
        # close                     267094722 samples [reqs]
        # create                    3639339 samples [reqs]
        # enqueue                   100020304 samples [reqs]
        # getattr                   1935909 samples [reqs]
        # intent_lock               2624814194 samples [reqs]
        # link                      5579059 samples [reqs]
        # rename                    2666193 samples [reqs]
        # setattr                   36255873 samples [reqs]
        # fsync                     288967 samples [reqs]
        # read_page                 45198320 samples [reqs]
        # unlink                    21058273 samples [reqs]
        # setxattr                  480869 samples [reqs]
        # getxattr                  19447312 samples [reqs]
        # revalidate_lock           425865270 samples [reqs]
        for metric_line in res_parts:
            if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
                tokens = str(metric_line).split(" ")
                md_stats_latest_values[tokens[0]] = float(tokens[len(tokens) - 3])
                # value_list.append(tokens[0])
                # value = float(tokens[len(tokens) - 3])
                # value_list.append(value)
        mdt_stat_latest_values["md_stats"] = md_stats_latest_values

        value_list.append(float((md_stats_latest_values.get("close") or 0) - (md_stats_so_far_dict.get("close") or 0)))
        value_list.append(float((md_stats_latest_values.get("create") or 0) - (md_stats_so_far_dict.get("create") or 0)))
        value_list.append(float((md_stats_latest_values.get("enqueue") or 0) - (md_stats_so_far_dict.get("enqueue") or 0)))
        value_list.append(float((md_stats_latest_values.get("getattr") or 0) - (md_stats_so_far_dict.get("getattr") or 0)))
        value_list.append(float((md_stats_latest_values.get("intent_lock") or 0) - (md_stats_so_far_dict.get("intent_lock") or 0)))
        value_list.append(float((md_stats_latest_values.get("link") or 0) - (md_stats_so_far_dict.get("link") or 0)))
        value_list.append(float((md_stats_latest_values.get("rename") or 0) - (md_stats_so_far_dict.get("rename") or 0)))
        value_list.append(float((md_stats_latest_values.get("setattr") or 0) - (md_stats_so_far_dict.get("setattr") or 0)))
        value_list.append(float((md_stats_latest_values.get("fsync") or 0) - (md_stats_so_far_dict.get("fsync") or 0)))
        value_list.append(float((md_stats_latest_values.get("read_page") or 0) - (md_stats_so_far_dict.get("read_page") or 0)))
        value_list.append(float((md_stats_latest_values.get("unlink") or 0) - (md_stats_so_far_dict.get("unlink") or 0)))
        value_list.append(float((md_stats_latest_values.get("setxattr") or 0) - (md_stats_so_far_dict.get("setxattr") or 0)))
        value_list.append(float((md_stats_latest_values.get("getxattr") or 0) - (md_stats_so_far_dict.get("getxattr") or 0)))
        value_list.append(float((md_stats_latest_values.get("ntent_getattr_async") or 0) - (md_stats_so_far_dict.get("ntent_getattr_async") or 0)))
        value_list.append(float((md_stats_latest_values.get("revalidate_lock") or 0) - (md_stats_so_far_dict.get("revalidate_lock") or 0)))

        return value_list, mdt_stat_latest_values

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
        message = ParseDict(self.get_metrics_list_to_dict_no_prefix(), ClientMdtMetrics())
        return message
