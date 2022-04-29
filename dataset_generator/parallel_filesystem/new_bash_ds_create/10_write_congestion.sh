#!/bin/bash

round_counter=1
max_round_number=2
main_sleep_time=60

user_name='root'

receiver_remote_client_ip=10.10.2.2
remote_client_ip=10.10.2.3

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on remote lustre client";
    ssh root@$remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;
}
kill_all_java_python3_processes(){
    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

    ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
    ssh root@$receiver_remote_client_ip 'killall -9  -u root java'
}
# write_congestion_by_clients_on_receiver
#congestions=([1]="write_congestion_by_clients_on_receiver_ost_1" [2]="write_congestion_by_clients_on_receiver_ost_2"
#[4]="write_congestion_by_clients_on_receiver_ost_4" [6]="write_congestion_by_clients_on_receiver_ost_6"
#[8]="write_congestion_by_clients_on_receiver_ost_8" [10]="write_congestion_by_clients_on_receiver_ost_10"
#[12]="write_congestion_by_clients_on_receiver_ost_12" [14]="write_congestion_by_clients_on_receiver_ost_14"
#[16]="write_congestion_by_clients_on_receiver_ost_16")

congestions=([1]="82" [2]="83" [4]="84" [6]="85" [8]="86" [10]="87" [12]="88" [14]="89" [16]="90")
while true
do
    printf "\n"
    echo "round number ${round_counter}"
    if [ $round_counter -gt $max_round_number ];then
       break
    fi
    for i in "${!congestions[@]}"; do
      clear_all_caches
      label=${congestions[$i]}
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py -l ${label} -jsp 50505 -jtl ${label}"&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/dstDataDir/diskWriteStress/ ${i}"&
      python3 ../parallel_metric_collector.py -l ${label}  -jsp 50505&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      ssh root@$remote_client_ip 'killall -9  -u root python3'
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done
