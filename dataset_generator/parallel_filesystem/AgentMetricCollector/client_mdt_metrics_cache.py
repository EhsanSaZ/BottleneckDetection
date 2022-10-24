from subprocess import Popen, PIPE
from multiprocessing import Process, Event
from zmq import ZMQError
import zmq
import requests
from cachetools import TTLCache
import re


class LustreClientMdtMetricCache(Process):
    def __init__(self, context, cache_size, cache_ttl, rep_backend_socket_name, **kwargs):
        super(LustreClientMdtMetricCache, self).__init__(**kwargs)
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
        print()
        self.backend_socket.bind("ipc://{}".format(self.rep_backend_socket_name))

    def reset_backend_socket(self):
        self.backend_socket.close()
        self.initialize_backend_socket()


    def start_server(self):
        self.initialize_backend_socket()
        while True and not self.stopped():
            try:
                data = self.backend_socket.recv_json()
                cache_key = "{}_{}".format(data["mdt_dir_name"], data["time_stamp"])
                response_body = self.cache.get(cache_key)

                if response_body is None:
                    requested_timestamp = data["time_stamp"]
                    cmd = "lctl get_param mdc.*.import; echo {seperator};lctl get_param mdc.*.stats;echo {seperator};lctl get_param mdc.*.md_stats".format(seperator=self.seperator_string)
                    proc = Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE)
                    res = proc.communicate()[0]
                    res_parts = res.split(self.seperator_string)
                    mdt_import_parts = res_parts[0]
                    mdt_stats_parts = res_parts[1]
                    mdt_md_stats_parts = res_parts[2]

                    import_list = re.split('(mdc\..*\.import=)', mdt_import_parts)
                    stats_list = re.split('(mdc\..*\.stats=)', mdt_stats_parts)
                    md_stats_list = re.split('(mdc\..*\.md_stats=)', mdt_md_stats_parts)

                    i = 0
                    while i < len(import_list):
                        _import = import_list[i]
                        if _import == '':
                            i += 1
                        else:
                            match = re.match(r"mdc.(?P<mdt_dir_name>.*).import=", _import)
                            if match:
                                _key = "{}_{}".format(match.groupdict().get('mdt_dir_name'), requested_timestamp)
                                self.cache[_key] = {"import": import_list[i + 1]}
                                i += 2
                            else:
                                i += 1
                    i = 0
                    while i < len(stats_list):
                        stat = stats_list[i]
                        if stat == '':
                            i += 1
                        else:
                            match = re.match(r"mdc.(?P<mdt_dir_name>.*).stats=", stat)
                            if match:
                                _key = "{}_{}".format(match.groupdict().get('mdt_dir_name'), requested_timestamp)
                                self.cache[_key].update({"stats": stats_list[i + 1]})
                                i += 2
                            else:
                                i += 1
                    i = 0
                    while i < len(md_stats_list):
                        md_stat = md_stats_list[i]
                        if md_stat =='':
                            i += 1
                        else:
                            match = re.match(r"mdc.(?P<mdt_dir_name>.*).md_stats=", md_stat)
                            if match:
                                _key = "{}_{}".format(match.groupdict().get('mdt_dir_name'), requested_timestamp)
                                self.cache[_key].update({"md_stats": md_stats_list[i + 1], "status": "success"})
                                i += 2
                            else:
                                i += 1
                    self.backend_socket.send_json(self.cache.get(cache_key))
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
