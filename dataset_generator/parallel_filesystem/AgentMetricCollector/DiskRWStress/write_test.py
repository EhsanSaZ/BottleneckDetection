import mmap
import os
import string
import time
import random
from subprocess import Popen
from threading import Thread
import sys
"""
This file is run by a bash script to put the disk under the stress of writing bytes
The argument is the number of threads
"""

# base_path = '/home/esaeedizade/Desktop/diskWriteStress/'
#
# if not base_path.endswith('/'):
#     base_path = base_path + "/"


class WriteThread(Thread):

    def __init__(self, filename, base_path):
        Thread.__init__(self)
        self.filename = filename
        self.base_path = base_path
        # 1024 bytes data - 1KB
        self.chars = rnd = os.urandom(131072)
    def run(self):
        while True:
            # strategy 1:
            proc = Popen(['touch', self.base_path + self.filename + ".txt"])
            proc.communicate()
            with open(self.base_path + self.filename + ".txt", 'wb', buffering=0) as f:
                for i in range(3145728):
                    f.write(self.chars)
                    # f.flush()
            # strategy 2:
            # m = mmap.mmap(-1, 1024)
            # fd = os.open(base_path + self.filename + ".txt", os.O_CREAT | os.O_DIRECT | os.O_WRONLY)
            # m.write(self.chars)
            # for i in range(1024):
            #     os.write(fd, m)
            # os.close(fd)
            proc2 = Popen(['rm', self.base_path + self.filename + ".txt"])
            proc2.communicate()


base_path = str(sys.argv[1])
thread_number = int(sys.argv[2])

if not base_path.endswith('/'):
    base_path = base_path + "/"

start_time = time.time()
threads = []
for x in range(thread_number):
    new_thread = WriteThread(str(x), base_path)
    new_thread.start()
    threads.append(new_thread)

for t in threads:
    t.join()

print("\n--- %s seconds ---" % (time.time() - start_time))
