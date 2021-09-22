import time
from subprocess import Popen
from threading import Thread
import sys
"""
This file is run by a bash script to put the disk under the stress of writing bytes
The argument is the number of threads
"""

base_path = '/home/esaeedizade/Desktop/diskWriteStress/'

if not base_path.endswith('/'):
    base_path = base_path + "/"


class WriteThread(Thread):

    def __init__(self, filename):
        Thread.__init__(self)
        self.filename = filename

    def run(self):
        while True:
            proc = Popen(['touch', base_path + self.filename])
            proc.communicate()
            proc2 = Popen(['rm', base_path + self.filename])
            proc2.communicate()


thread_number = int(sys.argv[1])
start_time = time.time()
threads = []
for x in range(thread_number):
    new_thread = WriteThread(str(x))
    new_thread.start()
    threads.append(new_thread)

for t in threads:
    t.join()

print("\n--- %s seconds ---" % (time.time() - start_time))
