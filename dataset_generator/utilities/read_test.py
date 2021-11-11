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
max_thread_name = 18
src_path = "/home/esaeedizade/Desktop/diskReadStress/"

if not src_path.endswith('/'):
    src_path = src_path + "/"


class ReadThread(Thread):

    def __init__(self, filename):
        Thread.__init__(self)
        self.folder_name = filename

    def run(self):
        all_files = glob.glob(src_path + self.folder_name + "/*")
        random.shuffle(all_files)
        # file_count = 0
        # proc = subprocess.run(['sudo ./clearCacheScript.sh'], universal_newlines=True, shell=True)
        while True:
            for file_ in all_files:
                proc = subprocess.run(['vmtouch -ve ' + str(file_)], stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                print("Reading " + file_)
                with open(file_, 'rb', buffering=0) as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                # file_count += 1
                # if file_count == len(all_files):
                #     print(" Start a new round")
                #     file_count = 0
                #     proc = subprocess.run(['sudo ./clearCacheScript.sh'], universal_newlines=True, shell=True)


thread_number = int(sys.argv[1])
start_time = time.time()
threads = []
for x in range(thread_number+1):
    new_thread = ReadThread(str(x % max_thread_name))
    new_thread.start()
    threads.append(new_thread)

for t in threads:
    t.join()

print("\n--- %s seconds ---" % (time.time() - start_time))
