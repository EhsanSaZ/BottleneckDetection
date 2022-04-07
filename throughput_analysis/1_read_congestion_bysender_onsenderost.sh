#!/bin/bash

user_name='root'
receiver_remote_client_ip=10.10.2.2

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

main_sleep_time=60

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
kill_all_java_processes(){
#    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

#    ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
    ssh root@$receiver_remote_client_ip 'killall -9  -u root java'
}

clear_all_caches
label='read_congestion_by_sender_sender_ost_0'
ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
sleep 5;
java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ 0 &
sleep $main_sleep_time;
kill_all_java_processes
killall -9  -u $user_name python3;

congestions=([1]="read_congestion_by_sender_sender_ost_1" [2]="read_congestion_by_sender_sender_ost_2"
[4]="read_congestion_by_sender_sender_ost_4" [6]="read_congestion_by_sender_sender_ost_6"
[8]="read_congestion_by_sender_sender_ost_8" [10]="read_congestion_by_sender_sender_ost_10"
[12]="read_congestion_by_sender_sender_ost_12" [14]="read_congestion_by_sender_sender_ost_14"
[16]="read_congestion_by_sender_sender_ost_16")

for i in "${!congestions[@]}"; do
#  printf "%s\t%s\n" "$i" "${congestions[$i]}"
  clear_all_caches
  label=${congestions[$i]}
  ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
  sleep 5;
  python3 /users/Ehsan/BottleneckDetection/dataset_generator/parallel_filesystem/AgentMetricCollector/DiskRWStress/read_test.py /lustre/dataDir/diskReadStress/ $i&
  java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ $i &
  sleep $main_sleep_time;
  kill_all_java_processes
  killall -9  -u $user_name python3;
  sleep 1;
done