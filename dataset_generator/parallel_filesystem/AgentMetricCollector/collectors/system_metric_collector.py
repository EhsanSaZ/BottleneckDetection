import traceback
from subprocess import Popen, PIPE


class SystemMetricCollector:

    def collect_system_metrics(self, pid_str, target_process):
        pid = int(pid_str.strip())

        value_list = []
        # create process to collect io metrics
        try:
            proc = Popen(['cat', '/proc/' + str(pid).strip() + '/io'], universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split("\n")
            for line in res_parts:
                if len(line.strip()) > 0:
                    index = line.rfind(":")
                    value = int(line[index + 1:].strip())
                    value_list.append(value)
        except:
            print("io stat not possible")
            traceback.print_exc()

        # create process to collect stat metrics
        try:
            proc = Popen(['cat', '/proc/' + str(pid).strip() + '/stat'], universal_newlines=True, stdout=PIPE)
            res = proc.communicate()[0]
            res_parts = res.split(" ")
            for line in res_parts:
                if len(line.strip()) > 0:
                    try:
                        value = int(line.strip())
                        value_list.append(value)
                    except:
                        # only convert numbers to int as pass error for other strings
                        pass
                        # traceback.print_exc()
        except:
            print("stat not possible")
            traceback.print_exc()

        # create process to collect cpu memory metrics
        try:
            value_list.append(float(target_process.cpu_percent()))
            value_list.append(float(target_process.memory_percent()))
            # proc = Popen(['ps', '-p', str(pid).strip(), '-o', '%cpu,%mem'], universal_newlines=True, stdout=PIPE)
            # res = proc.communicate()[0]
            # res_parts = res.split("\n")
            # for line in res_parts:
            #     if len(line.strip()) > 0:
            #         if "%CPU" not in line:
            #             parts = line.split(" ")
            #             for x in parts:
            #                 if len(x.strip()) > 0:
            #                     value_list.append(float(x))
        except:
            traceback.print_exc()
            print("cpu mem is not possible")

        return value_list
