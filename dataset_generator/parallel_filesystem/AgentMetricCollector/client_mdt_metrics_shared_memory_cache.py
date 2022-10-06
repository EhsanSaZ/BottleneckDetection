import time
import traceback
from subprocess import Popen, PIPE
from multiprocessing import Process, Event
import re


class LustreClientMdtMetricSharedMemCache(Process):
    def __init__(self, client_mdt_metrics_dict, sleep_time, **kwargs):
        super(LustreClientMdtMetricSharedMemCache, self).__init__(**kwargs)
        self.client_mdt_metrics_dict = client_mdt_metrics_dict
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

                temp_dict = {}
                i = 0
                while i < len(import_list):
                    _import = import_list[i]
                    if _import == '':
                        i += 1
                    else:
                        match = re.match(r"mdc.(?P<mdt_dir_name>.*).import=", _import)
                        if match:
                            _key = "{}".format(match.groupdict().get('mdt_dir_name'))
                            temp_dict[_key] = {"import": import_list[i + 1]}
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
                            _key = "{}".format(match.groupdict().get('mdt_dir_name'))
                            temp_dict[_key].update({"stats": stats_list[i + 1]})
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
                            _key = "{}".format(match.groupdict().get('mdt_dir_name'))
                            temp_dict[_key].update({"md_stats": md_stats_list[i + 1]})
                            i += 2
                        else:
                            i += 1
                for _key in temp_dict.keys():
                    self.client_mdt_metrics_dict[_key] = temp_dict[_key]
                time.sleep(self.sleep_time)
            except Exception as e:
                traceback.print_exc()
                print(str(e))
                time.sleep(self.sleep_time)
