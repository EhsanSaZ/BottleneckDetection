import threading
import traceback
from multiprocessing import Process, Event

import zmq
import requests
from cachetools import TTLCache
from zmq import ZMQError


class LustreOstMetricCache(Process):
    def __init__(self, context,  cache_size, cache_ttl, rep_backend_socket_name, remote_ost_index_to_ost_agent_http_address_dict, **kwargs):
        # threading.Thread.__init__(self)
        super(LustreOstMetricCache, self).__init__(**kwargs)
        self._stop = Event()
        self.context = context
        self.backend_socket = None
        self.rep_backend_socket_name = rep_backend_socket_name
        # self.frontend_socket = self.context.socket(zmq.REQ)
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.remote_ost_index_to_ost_agent_http_address_dict = remote_ost_index_to_ost_agent_http_address_dict

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
                    ost_number = data["ost_number"]
                    ost_agent_address = self.remote_ost_index_to_ost_agent_http_address_dict.get(ost_number) or ""
                    if ost_agent_address != "":
                        path = "obdfilter." + data["ost_dir_name"] + ".stats"
                        response = requests.post(ost_agent_address + "lctl_get_param", json={"path": path})
                        response_body = response.json()
                    else:
                        response_body = {"out_put": "", "error": "No address found for ost index {}".format(ost_number)}
                    self.cache[cache_key] = response_body
                    self.backend_socket.send_json(response_body)
                else:
                    self.backend_socket.send_json(response_body)
            except ZMQError as e:
                # traceback.print_exc()
                print(str(e))
                self.reset_backend_socket()
            except Exception as e:
                # traceback.print_exc()
                print(str(e))
                self.backend_socket.send_json({"out_put": "", "error": str(e)})
