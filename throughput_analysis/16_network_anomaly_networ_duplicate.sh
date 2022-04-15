#!/bin/bash

user_name='root'
receiver_remote_client_ip=10.10.2.2
#remote_client_ip=10.10.2.3
#other_oss_server_ip=10.10.1.4

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

ethernet_interface_name='p1p1'

main_sleep_time=60

clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
#    echo "Clearing cache on other oss server";
#    ssh root@$other_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

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
label='network_anomaly_network_duplicate_0'
ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
sleep 5;
java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ 0 &
sleep $main_sleep_time;
kill_all_java_processes
killall -9  -u $user_name python3;
sleep 1;

label_general="network_anomaly_network_duplicate_"
levels=([1]=10 [2]=15 [3]=20 [4]=25 [5]=30 [6]=35 [7]=40 [8]=45 [9]=50 [10]=55 [11]=60 [12]=65)

for i in "${!levels[@]}"; do
#  printf "%s\t%s\n" "$i" "${levels[$i]}"
  clear_all_caches
  label=${label_general}${levels[$i]}
  echo $label
  ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
  tc qdisc add dev $ethernet_interface_name root netem duplicate ${levels[$i]}%;
  sleep 5;
  java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ $i &
  sleep $main_sleep_time;
  kill_all_java_processes
  tc qdisc del dev $ethernet_interface_name root;
  sleep 1;
done