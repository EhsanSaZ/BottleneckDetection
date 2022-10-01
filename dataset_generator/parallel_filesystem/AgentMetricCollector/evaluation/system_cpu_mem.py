import threading
import argparse

import psutil
import time

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--file_name', help="output file name", required=True)

args = parser.parse_args()
output_file_name = args.file_name


class fileWriteThread(threading.Thread):
    def __init__(self, metric_string, file_path_prefix):
        threading.Thread.__init__(self)
        self.metric_string = metric_string
        self.file_path_prefix = file_path_prefix

    def run(self):
        output_file = open("{}.csv".format(self.file_path_prefix), "a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


epoc_count = 0
output_string = ""
cpu_usage = psutil.cpu_percent()
mem_usage = psutil.virtual_memory().percent
time.sleep(1)
while True:
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    output_string += "{},{}\n".format(cpu_usage, mem_usage)
    epoc_count += 1
    # print(psutil.cpu_percent(), psutil.virtual_memory().percent)
    if epoc_count % 10 == 0:
        write_thread = fileWriteThread(output_string, "CPU_MEM_USAGE_{}".format(output_file_name))
        write_thread.start()
        output_string = ""
    if epoc_count == 60:
        break
    time.sleep(1)

