#!/bin/bash
transfer_time=0
ethernet_interface_name='enp1s0f0'
user_name='root'
receiver_remote_client_ip=10.10.1.5
sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3
main_sleep_time=30
maximum_transfer_time_seconds=240
clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;
}

kill_all_java_python3_processes(){
    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

    ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
    ssh root@$receiver_remote_client_ip 'killall -9  -u root java'
}
trap kill_all_java_python3_processes EXIT

while true
do
  printf "\n"
    echo "transfer_time ${round_counter}"
    if [ $transfer_time -gt $maximum_transfer_time_seconds ];then
       break
    fi
    clear_all_caches

    uuid=$(uuidgen)
    echo "Run the java server on receiver side and start metric collector agent";
    ssh root@$receiver_remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 0 ${uuid}"&
    sleep 5;

    echo "Start collecting metrics on sender side";
    python3 parallel_metric_collector.py 0 $uuid&

    sleep $main_sleep_time;

    kill_all_java_python3_processes

    transfer_time=$((transfer_time+main_sleep_time));
    sleep 5;
done