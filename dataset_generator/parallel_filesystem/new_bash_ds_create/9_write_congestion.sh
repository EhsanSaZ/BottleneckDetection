#!/bin/bash

round_counter=1
max_round_number=2
main_sleep_time=60

user_name='root'

receiver_remote_client_ip=10.10.2.2
remote_client_ip=10.10.2.3

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

ethernet_interface_name='p1p2'
network_bw=1024mbit
limited_bw=false
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
# write_congestion_by_receiver_on_receiver
#congestions=([1]="write_congestion_by_receiver_on_receiver_ost_1" [2]="write_congestion_by_receiver_on_receiver_ost_2"
#[4]="write_congestion_by_receiver_on_receiver_ost_4" [6]="write_congestion_by_receiver_on_receiver_ost_6"
#[8]="write_congestion_by_receiver_on_receiver_ost_8" [10]="write_congestion_by_receiver_on_receiver_ost_10"
#[12]="write_congestion_by_receiver_on_receiver_ost_12" [14]="write_congestion_by_receiver_on_receiver_ost_14"
#[16]="write_congestion_by_receiver_on_receiver_ost_16")

congestions=([1]="73" [2]="74" [4]="75" [6]="76" [8]="77" [10]="78" [12]="79" [14]="80" [16]="81")
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
      if $limited_bw
      then
        sudo tc qdisc add dev $ethernet_interface_name root netem rate ${network_bw};
      fi
      sleep 5;
      ssh root@$receiver_remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/dstDataDir/diskWriteStress/ ${i}"&
      echo "Start collecting metrics on sender side";
      python3 ../parallel_metric_collector.py -l ${label}  -jsp 50505&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
#      ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done