from subprocess import Popen, PIPE

from global_cache import ost_metrics_dict
from multiprocessing import Process, Event
import time
import traceback
import re

class LustreOStCache(Process):
    def __init__(self, ost_metrics_dict, sleep_time, **kwargs):
        super(LustreOStCache, self).__init__(**kwargs)
        self.ost_metrics_dict = ost_metrics_dict
        self.sleep_time = sleep_time
        self._stop = Event()
        self.seperator_string = '--result--'

    def run(self):
        self.start_collection()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def start_collection(self):
        while True and not self.stopped():
            try:
                d = {"time": time.time()}
                proc = Popen(['lctl', 'get_param', 'obdfilter.*.stats'], universal_newlines=True, stdout=PIPE, stderr=PIPE)
                obd_filter_response = proc.communicate()[0]

                obdfilter_stats_list = re.split('(obdfilter\..*\.stats=)', obd_filter_response)
                temp_dict = {}
                i = 0
                while i < len(obdfilter_stats_list):
                    stat = obdfilter_stats_list[i]
                    if stat == '':
                        i += 1
                    else:
                        match = re.match(r"obdfilter.(?P<ost_dir_name>.*).stats=", stat)
                        if match:
                            _key = "{}".format(match.groupdict().get('ost_dir_name'))
                            temp_dict[_key] = {"stats": obdfilter_stats_list[i + 1]}
                            i += 2
                        else:
                            i += 1
                for _key in temp_dict.keys():
                    self.ost_metrics_dict[_key] = temp_dict[_key]
                time.sleep(self.sleep_time)
            except Exception as e:
                traceback.print_exc()
                print(str(e))
                time.sleep(self.sleep_time)
