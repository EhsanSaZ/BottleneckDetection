#!/bin/bash

round_counter=1
max_round_number=2
main_sleep_time=60

user_name='root'

receiver_remote_client_ip=10.10.2.2

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

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
# read_congestion_by_sender_sender_ost
#congestions=([1]="read_congestion_by_sender_sender_ost_1" [2]="read_congestion_by_sender_sender_ost_2"
#[4]="read_congestion_by_sender_sender_ost_4" [6]="read_congestion_by_sender_sender_ost_6"
#[8]="read_congestion_by_sender_sender_ost_8" [10]="read_congestion_by_sender_sender_ost_10"
#[12]="read_congestion_by_sender_sender_ost_12" [14]="read_congestion_by_sender_sender_ost_14"
#[16]="read_congestion_by_sender_sender_ost_16")

congestions=([1]="1" [2]="2" [4]="3" [6]="4" [8]="5" [10]="6" [12]="7" [14]="8" [16]="9")
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
      python3 /users/Ehsan/BottleneckDetection/dataset_generator/parallel_filesystem/AgentMetricCollector/DiskRWStress/read_test.py /lustre/dataDir/diskReadStress/ $i&
      python3 ../parallel_metric_collector.py -l ${label}  -jsp 50505&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done