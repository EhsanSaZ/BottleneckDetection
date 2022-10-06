import time
import traceback
from subprocess import Popen, PIPE
from multiprocessing import Process, Event
import re


class LustreClientOstMetricSharedMemCache(Process):
    def __init__(self, client_ost_metrics_dict, sleep_time, **kwargs):
        super(LustreClientOstMetricSharedMemCache, self).__init__(**kwargs)
        self.client_ost_metrics_dict = client_ost_metrics_dict
        self.sleep_time = sleep_time
        self._stop = Event()
        self.seperator_string = '--result--'

    def run(self):
        self.start_server()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def start_server(self):
        while True and not self.stopped():
            try:
                # self.client_ost_metrics_dict["time"] = time.time()
                cmd = "lctl get_param osc.*.stats; echo {seperator};lctl get_param osc.*.rpc_stats".format(
                    seperator=self.seperator_string)
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
                            _key = "{}".format(match.groupdict().get('ost_dir_name'))
                            self.client_ost_metrics_dict[_key] = {"stats": stats_list[i + 1]}
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
                            _key = "{}".format(match.groupdict().get('ost_dir_name'))
                            self.client_ost_metrics_dict[_key].update(
                                {"rpc_stats": rpc_stats_list[i + 1], "status": "success"})
                            i += 2
                        else:
                            i += 1

                time.sleep(self.sleep_time)
            except Exception as e:
                traceback.print_exc()
                print(str(e))
                time.sleep(self.sleep_time)