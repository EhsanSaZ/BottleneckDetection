#!/bin/bash

user_name='root'
receiver_remote_client_ip=10.10.2.2
remote_client_ip=10.10.2.3
other_oss_server_ip=10.10.1.4

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

main_sleep_time=60

clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on other oss server";
    ssh root@$other_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
#    echo "Clearing cache on remote lustre client";
#    ssh root@$remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
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
label='write_congestion_by_receiver_on_other_ost_0'
ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
sleep 5;
java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ 0 &
sleep $main_sleep_time;
kill_all_java_processes
killall -9  -u $user_name python3;
sleep 1;

congestions=([1]="write_congestion_by_receiver_on_other_ost_1" [2]="write_congestion_by_receiver_on_other_ost_2"
[4]="write_congestion_by_receiver_on_other_ost_4" [6]="write_congestion_by_receiver_on_other_ost_6"
[8]="write_congestion_by_receiver_on_other_ost_8" [10]="write_congestion_by_receiver_on_other_ost_10"
[12]="write_congestion_by_receiver_on_other_ost_12" [14]="write_congestion_by_receiver_on_other_ost_14"
[16]="write_congestion_by_receiver_on_other_ost_16")

for i in "${!congestions[@]}"; do
#  printf "%s\t%s\n" "$i" "${congestions[$i]}"
  clear_all_caches
  label=${congestions[$i]}
  ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
  ssh root@$receiver_remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/clientData/diskWriteStress/ ${i}"&
  sleep 5;
#  python3 /users/Ehsan/BottleneckDetection/dataset_generator/parallel_filesystem/AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ $i&
  java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ $i &
  sleep $main_sleep_time;
  kill_all_java_processes
  ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
#  killall -9  -u $user_name python3;
  sleep 1;
done