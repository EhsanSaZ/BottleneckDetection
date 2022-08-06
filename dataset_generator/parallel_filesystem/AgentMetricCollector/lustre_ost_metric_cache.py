import threading
import traceback

import zmq
import requests
from cachetools import TTLCache
from zmq import ZMQError


class LustreOstMetricCache(threading.Thread):
    def __init__(self, cache_size, cache_ttl, rep_backend_socket_name, remote_ost_index_to_ost_agent_http_address_dict):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.context = zmq.Context()
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
        return self._stop.isSet()

    def initialize_backend_socket(self):
        self.backend_socket = self.context.socket(zmq.REP)
        self.backend_socket.bind("inproc://{}".format(self.rep_backend_socket_name))

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
                traceback.print_exc()
                self.reset_backend_socket()
            except Exception as e:
                traceback.print_exc()
                self.backend_socket.send_json({"out_put": "", "error": str(e)})
