# Follow instructions before run normal_filesystem dataset generator
## Prepare environments
1- create a srcData directory and generate some large binary files inside it.<br />
2- Set src_path in normal_filesystem/metric_collector.py to the absolute path of srcData directory.<br />

3- create a dstData directory on the receiver side, before running simple Receiver.<br />
4- Set dst_path in normal_filesystem/metric_collector.py to the absolute path of dstData directory.<br />

5- Create a diskReadStress directory and set the src_path in utilities/read_test.py to the absolute path of diskReadStress<br />
6- Create at least 16 directories in diskReadStress directory, named them 1...16.<br />
7- Create at least 5 large file (1GB size) in each of 16 directories and name each file as below:<br />
file_<directory_number>_file_number<br /><br />

8- Create a diskWriteStress directory and set the base_path in utilities/write_test.py to the absolute path of diskWriteStress<br />

9- Set src_ip, dst_ip, port_number, time_length, drive_name in the normal_filesystem/metric_collector.py as below:<br />
* Ip address of the host that metric collector is run on it: use 127.0.0.0 for local host.
* Ip address of the host/server that simplereceiver1.java is run on it
* Port number that simplereceiver1.java is listening on it. 
* name of the hard drive that we are reading/writing data and collects metrics from it.

10- create a python virtual environment and install the requirements.txt
11- install stress, stress-ng, vmtouch(https://hoytech.com/vmtouch/) if they are not installed on the host that metric collector is run