import random
import subprocess

# creating transfers from one source to all other sources
import time

dtn_number_ip_dict = {1: "10.10.2.2", 2: "10.10.2.3", 3: "10.10.2.4", 4: "10.10.2.5", 5: "10.10.2.6",
                      6: "10.10.2.7", 7: "10.10.2.8", 8: "10.10.2.9", 9: "10.10.2.10"}


def kill_servers_and_run():
    host_tmp = "root@node{}"
    kill_server_command = 'killall -9 globus-gridftp-server'
    for dtn_number in dtn_number_ip_dict.keys():
        print("kill globus server on DTN {}".format(dtn_number))
        host = host_tmp.format(dtn_number)
        proc = subprocess.Popen(['ssh', host, kill_server_command], stdout=subprocess.DEVNULL)
    print("sleep fot 5 seconds")
    time.sleep(5)
    run_server_command_tmp = 'cd /users/Ehsan/SetupIns/globusConf/; globus-gridftp-server -c gridftp.conf -aa --data-interface {ip} -p 50000 -s -S'
    for dtn_number in dtn_number_ip_dict.keys():
        print("run globus server on DTN {}".format(dtn_number))
        host = host_tmp.format(dtn_number)
        run_server_command = run_server_command_tmp.format(ip=dtn_number_ip_dict[dtn_number])
        proc = subprocess.Popen(['ssh', host, run_server_command], stdout=subprocess.DEVNULL)


kill_servers_and_run()
print("globus server is running on port 50000 on all DTNs")

def run_transfers():
    total_transfers_number = 2
    for source in dtn_number_ip_dict.keys():
        source_dtn_number = source
        run_client_command = 'cd /users/Ehsan/SetupIns/globusConf/;'
        globus_url_copy_command_temp = 'nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:50000/lustre/{dtn_folder}/writeFolder/ > /dev/null & '
        i = 0
        while i < total_transfers_number:
            destination_dtn_number = random.randint(1, 10)
            if destination_dtn_number != source_dtn_number:
                source_dtn_host = "root@node{}".format(source_dtn_number)
                destination_dtn_ip = dtn_number_ip_dict[destination_dtn_number]
                globus_url_copy_command = globus_url_copy_command_temp.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number)
                print("preparing transfer {} on DTN {}".format(i, source_dtn_number))
                print(globus_url_copy_command)
                run_client_command += globus_url_copy_command
                # run_client_command = 'cd /users/Ehsan/SetupIns/globusConf/;  nohup globus-url-copy /lustre/{src_folder}/readFolder/15Gfile ftp://{dst_ip}:50000/lustre/{dtn_folder}/writeFolder/ > /dev/null &'.format(src_folder=source_dtn_number, dst_ip=destination_dtn_ip, dtn_folder=destination_dtn_number)
                # print(source_dtn_host, run_client_command)
            else:
                i -= 1
            i += 1
        print(run_client_command)
        proc = subprocess.Popen(['ssh', source_dtn_host, run_client_command], stdout=subprocess.DEVNULL)
time.sleep(5)
run_transfers()



