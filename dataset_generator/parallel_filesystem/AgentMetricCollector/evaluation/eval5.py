import random
import subprocess

# creating transfers from one source to all other sources
import time

dtn_number_ip_dict = {1: "10.10.2.2", 2: "10.10.2.3", 3: "10.10.2.4", 4: "10.10.2.5", 5: "10.10.2.6",
                      6: "10.10.2.7", 7: "10.10.2.8", 8: "10.10.2.9", 9: "10.10.2.10", 10: "10.10.2.11"}


port_list = [50000, 51000, 52000]
destination_dtn_number_list = [2,3]

def kill_servers_and_run():
    host_tmp = "root@node{}"
    kill_server_command = 'killall -9 globus-gridftp-server'
    for dtn_number in dtn_number_ip_dict.keys():
        print("kill globus server on DTN {}".format(dtn_number))
        host = host_tmp.format(dtn_number)
        proc = subprocess.Popen(['ssh', host, kill_server_command], stdout=subprocess.DEVNULL)
    print("sleep fot 5 seconds")
    time.sleep(5)
    run_server_command_tmp = 'cd /users/Ehsan/SetupIns/globusConfig/; globus-gridftp-server -c gridftp.conf -aa --data-interface {ip} -p {port} -s -S'
    # run_server_command_tmp_2 = 'cd /users/Ehsan/SetupIns/globusConf/; globus-gridftp-server -c gridftp.conf -aa --data-interface {ip} -p 51000 -s -S'
    # run_server_command_tmp_3 = 'cd /users/Ehsan/SetupIns/globusConf/; globus-gridftp-server -c gridftp.conf -aa --data-interface {ip} -p 52000 -s -S'
    # commands = [run_server_command_tmp, run_server_command_tmp_2, run_server_command_tmp_3]

    for dtn_number in dtn_number_ip_dict.keys():
        for port in port_list:
            print("run globus server on DTN {}".format(dtn_number))
            host = host_tmp.format(dtn_number)
            run_server_command = run_server_command_tmp.format(ip=dtn_number_ip_dict[dtn_number], port=port)
            proc = subprocess.Popen(['ssh', host, run_server_command], stdout=subprocess.DEVNULL)

kill_servers_and_run()
print("globus server is running on port 50000, 51000, 52000 on all DTNs")

# def run_transfers():
#     source_dtn_number = 1
#     total_transfers_number = 2
#     run_client_command = 'cd /users/Ehsan/SetupIns/globusConf/;'
#     globus_url_copy_command_temp = 'nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:50000/lustre/{dtn_folder}/writeFolder/ > /dev/null & '
#     time.sleep(5)
#
#     for i in range(total_transfers_number):
#         destination_dtn_number = random.randint(2, 10)
#         source_dtn_host = "root@node{}".format(source_dtn_number)
#         destination_dtn_ip = dtn_number_ip_dict[destination_dtn_number]
#         globus_url_copy_command = globus_url_copy_command_temp.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number)
#         print("starting transfer {}".format(i))
#         print(globus_url_copy_command)
#         run_client_command += globus_url_copy_command
#         # run_client_command = 'cd /users/Ehsan/SetupIns/globusConf/;  nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:50000/lustre/{dtn_folder}/writeFolder/ > /dev/null &'.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number)
#         # print(source_dtn_host, run_client_command)
#     print(run_client_command)
#     proc = subprocess.Popen(['ssh', source_dtn_host, run_client_command], stdout=subprocess.DEVNULL)

# for b in range(15):
#     print("RUN batch number ", b)
#     run_transfers()
#     time.sleep(10)

def run_transfers(port, destination_dtn_number):
    source_dtn_number = 1
    total_transfers_number = 2
    run_client_command = 'cd /users/Ehsan/SetupIns/globusConfig/;'
    globus_url_copy_command_temp = 'nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:{port}/lustre/{dtn_folder}/writeFolder/ > /dev/null & '
    time.sleep(5)

    for i in range(total_transfers_number):
        # destination_dtn_number = random.randint(2, 10)
        source_dtn_host = "root@node{}".format(source_dtn_number)
        destination_dtn_ip = dtn_number_ip_dict[destination_dtn_number]
        globus_url_copy_command = globus_url_copy_command_temp.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number, port=port)
        print("starting transfer {}".format(i))
        print(globus_url_copy_command)
        run_client_command += globus_url_copy_command
        # run_client_command = 'cd /users/Ehsan/SetupIns/globusConf/;  nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:50000/lustre/{dtn_folder}/writeFolder/ > /dev/null &'.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number)
        # print(source_dtn_host, run_client_command)
    print(run_client_command)
    proc = subprocess.Popen(['ssh', source_dtn_host, run_client_command], stdout=subprocess.DEVNULL)


for port in port_list:
    for destination_dtn_number in destination_dtn_number_list:
        run_transfers(port, destination_dtn_number)
        time.sleep(10)

