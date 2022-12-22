import glob
import os
import subprocess
import time
from threading import Thread
import sys
import random
"""
This file is run by a bash script to put the disk under the stress of reading bytes
The argument is the number of threads
"""
BUFFER_SIZE = 1024 * 512
max_thread_name = 17
# src_path = "/home/esaeedizade/Desktop/diskReadStress/"
#
# if not src_path.endswith('/'):
#     src_path = src_path + "/"

Gbps = 1024 * 1024 * 1024 / 8
class ReadThread(Thread):

    def __init__(self, filename, src_path):
        Thread.__init__(self)
        self.folder_name = filename
        self.src_path = src_path

    def run(self):
        all_files = glob.glob(self.src_path + self.folder_name + "/*")
        random.shuffle(all_files)
        # file_count = 0
        # proc = subprocess.run(['sudo ./clearCacheScript.sh'], universal_newlines=True, shell=True)
        while True:
            for file_ in all_files:
                proc = subprocess.run(['vmtouch -ve ' + str(file_)], stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                print("Reading " + file_)
                with open(file_, 'rb', buffering=0) as f:
                    t1 = -1
                    read_size = 0
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        now = time.time()
                        read_size += BUFFER_SIZE
                        if now - t1 >= 1:
                            print("throughput is {} Gbps/s".format((read_size/Gbps) / (now - t1)))
                            t1 = time.time()
                            read_size = 0

                # file_count += 1
                # if file_count == len(all_files):
                #     print(" Start a new round")
                #     file_count = 0
                #     proc = subprocess.run(['sudo ./clearCacheScript.sh'], universal_newlines=True, shell=True)


src_path = str(sys.argv[1])
thread_number = int(sys.argv[2])

if not src_path.endswith('/'):
    src_path = src_path + "/"

start_time = time.time()
threads = []
for x in range(thread_number):
    new_thread = ReadThread(str((x+1) % max_thread_name), src_path)
    new_thread.start()
    threads.append(new_thread)

for t in threads:
    t.join()

print("\n--- %s seconds ---" % (time.time() - start_time))
