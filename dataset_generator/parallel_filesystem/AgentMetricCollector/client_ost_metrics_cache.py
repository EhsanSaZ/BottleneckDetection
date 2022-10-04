from subprocess import Popen, PIPE
from multiprocessing import Process, Event
from zmq import ZMQError
import zmq
import requests
from cachetools import TTLCache
import re

class LustreClientOstMetricCache(Process):
    def __init__(self, context, cache_size, cache_ttl, rep_backend_socket_name, **kwargs):
        super(LustreClientOstMetricCache, self).__init__(**kwargs)
        self._stop = Event()
        self.context = context
        self.backend_socket = None
        self.rep_backend_socket_name = rep_backend_socket_name
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.seperator_string = '--result--'

    def run(self):
        self.start_server()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def initialize_backend_socket(self):
        self.backend_socket = self.context.socket(zmq.REP)
        self.backend_socket.bind("ipc://{}".format(self.rep_backend_socket_name))

    def reset_backend_socket(self):
        self.backend_socket.close()
        self.initialize_backend_socket()

    def start_server(self):
        self.initialize_backend_socket()
        while True and not self.stopped():
            try:
                data = self.backend_socket.recv_json()
                cache_key = "{}_{}".format(data["ost_dir_name"], data["time_stamp"])
                response_body = self.cache.get(cache_key)
                if response_body is None:
                    requested_timestamp = data["time_stamp"]
                    cmd = "lctl get_param osc.*.stats; echo {seperator};lctl get_param osc.*.rpc_stats".format(seperator=self.seperator_string)
                    proc = Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE)
                    res = proc.communicate()[0]
                    res_parts = res.split(self.seperator_string)
                    ost_stats_parts = res_parts[0]
                    rpc_stats_part = res_parts[1]
                    stats_list = re.split('(osc\..*\.stats=)', ost_stats_parts)
                    rpc_stats_list = re.split('(osc\..*\.rpc_stats=)', rpc_stats_part)
                    i = 0
                    while i < len(stats_list):
                        stat = stats_list[i]
                        if stat == '':
                            i += 1
                        else:
                            match = re.match(r"osc.(?P<ost_dir_name>.*).stats=", stat)
                            if match:
                                # print(match.groupdict().get('ost_dir_name'), stats_list[i + 1])
                                _key = "{}_{}".format(match.groupdict().get('ost_dir_name'), requested_timestamp)
                                self.cache[_key] = {"stats": stats_list[i + 1]}
                                i += 2
                            else:
                                i += 1
                    i = 0
                    while i < len(rpc_stats_list):
                        rpc_stat = rpc_stats_list[i]
                        if rpc_stat == '':
                            i += 1
                        else:
                            match = re.match(r"osc.(?P<ost_dir_name>.*).rpc_stats=", rpc_stat)
                            if match:
                                _key = "{}_{}".format(match.groupdict().get('ost_dir_name'), requested_timestamp)
                                self.cache[_key].update({"rpc_stats": stats_list[i + 1], "status": "success"})
                                i += 2
                            else:
                                i += 1
                    self.backend_socket.send_json(self.cache.get(cache_key))
                #     ost_number = data["ost_number"]
                #     ost_agent_address = self.remote_ost_index_to_ost_agent_http_address_dict.get(ost_number) or ""
                #     if ost_agent_address != "":
                #         path = "obdfilter." + data["ost_dir_name"] + ".stats"
                #         response = requests.post(ost_agent_address + "lctl_get_param", json={"path": path})
                #         response_body = response.json()
                #     else:
                #         response_body = {"out_put": "", "error": "No address found for ost index {}".format(ost_number)}
                #     self.cache[cache_key] = response_body
                #     self.backend_socket.send_json(response_body)
                else:
                    self.backend_socket.send_json(response_body)

            except ZMQError as e:
                # traceback.print_exc()
                print(str(e))
                self.reset_backend_socket()
            except Exception as e:
                # traceback.print_exc()
                print(str(e))
                self.backend_socket.send_json({"status": "error", "error": str(e)})

# obj = LustreClientOstMetricCache(zmq.Context(), 1000, 10, "client_ost_metrics_test")
# obj.start()