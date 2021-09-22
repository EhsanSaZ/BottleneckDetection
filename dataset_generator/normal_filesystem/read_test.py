import glob
import time
from threading import Thread
import sys
"""
This file is run by a bash script to put the disk under the stress of reading bytes
The argument is the number of threads
"""
BUFFER_SIZE = 1024
max_thread_name = 18
src_path = "/home/esaeedizade/Desktop/diskReadStress/"

if not src_path.endswith('/'):
    src_path = src_path + "/"


class ReadThread(Thread):

    def __init__(self, filename):
        Thread.__init__(self)
        self.filename = filename

    def run(self):
        all_files = glob.glob(src_path + "*")
        while True:
            for file_ in all_files:
                with open(file_, 'rb') as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                print("done", self.filename)


thread_number = int(sys.argv[1])
start_time = time.time()
threads = []
for x in range(thread_number):
    new_thread = ReadThread(str(x % max_thread_name))
    new_thread.start()
    threads.append(new_thread)

for t in threads:
    t.join()

print("\n--- %s seconds ---" % (time.time() - start_time))
