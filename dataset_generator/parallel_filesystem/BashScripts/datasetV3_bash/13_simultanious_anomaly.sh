#!/bin/bash

round_counter=1
max_round_number=4
main_sleep_time=50

user_name='root'

receiver_ip=10.10.2.2

server1=10.10.1.2
server2=10.10.1.3
server3=10.10.1.4
server4=10.10.1.5
server5=10.10.1.6
server6=10.10.1.7
server7=10.10.1.8
server8=10.10.1.9

remote_client1_ip=10.10.2.3
remote_client2_ip=10.10.2.4
remote_client3_ip=10.10.2.5

ethernet_interface_name='enp6s0f1'
network_bw=1024mbit
limited_bw=false


clear_OSS_cache(){
    echo "Clearing cache on receiver oss server1";
    ssh root@$server1 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver oss server2";
    ssh root@$server2 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver oss server3";
    ssh root@$server3 'sync; echo 3 > /proc/sys/vm/drop_caches';

#    echo "Clearing cache on receiver oss server4";
#    ssh root@$server4 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server5";
#    ssh root@$server5 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server6";
#    ssh root@$server6 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server7";
#    ssh root@$server7 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server8";
#    ssh root@$server8 'sync; echo 3 > /proc/sys/vm/drop_caches';
}



clear_all_caches() {
    clear_OSS_cache
    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;

    echo "Clearing cache on other lustre clients";
    ssh root@$remote_client1_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    ssh root@$remote_client2_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    ssh root@$remote_client2_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
}


kill_all_java_python3_processes(){
    ssh root@$receiver_ip 'killall -9  -u root python3'
    ssh root@$receiver_ip 'killall -9  -u root java'

    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

}
# OST_read_congestion_by_clients_sender_ost
#types=([1]="read_congestion_by_clients_on_sender_ost_1" [2]="read_congestion_by_clients_on_sender_ost_2"
#[3]="read_congestion_by_clients_on_sender_ost_3")

types=([1]="49" [2]="50" [3]="51")
while true
do
    printf "\n"
    echo "round number ${round_counter}"
    if [ $round_counter -gt $max_round_number ];then
       break
    fi
    for i in "${!types[@]}"; do
      clear_all_caches
      label=${types[$i]}
      echo "Run the java server on receiver side and start metric collector agent\n";
      ssh root@$receiver_ip "python3 /users/Ehsan/AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 2 -jsp 50505 -jtl ${label}"&
      if $limited_bw
      then
#        sudo tc qdisc add dev $ethernet_interface_name root netem rate ${network_bw};
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 30ms;
      fi
      sleep 8;

      if [ ${i} == "1" ]; then
         echo "Congestion with 1 client"
         ssh root@$remote_client1_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/read_test.py /lustre/OST_0/diskReadStress/cli_1 1"&

         ssh root@$remote_client2_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/OST_1/diskWriteStress/cli2 1"&
         ssh root@$remote_client3_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/OST_1/diskWriteStress/cli3 1"&
      fi
      if [ ${i} == "2" ]; then
         echo "Congestion with 2 client"
         ssh root@$remote_client1_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/read_test.py /lustre/OST_0/diskReadStress/cli_1 1"&
         tc qdisc add dev $ethernet_interface_name root netem loss 1.2%;
      fi
      if [ ${i} == "3" ]; then
         echo "Congestion with 2 client"
         ssh root@$remote_client1_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/read_test.py /lustre/OST_0/diskReadStress/cli_1 1"&
         ssh root@$remote_client2_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/read_test.py /lustre/OST_0/diskReadStress/cli_2 1"&
         ssh root@$remote_client3_ip "python3 /users/Ehsan/AgentMetricCollector/DiskRWStress/write_test.py /lustre/OST_1/diskWriteStress/cli3 1"&

      fi

      echo "Run the Java client on sender side and Start metric collector agent";
      python3 ../../AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 1 -jlp 50521 -jtl ${label}&

      sleep $main_sleep_time;
      kill_all_java_python3_processes

      if [ ${i} == "1" ]; then
         ssh root@$remote_client1_ip 'killall -9  -u root python3'
         ssh root@$remote_client2_ip 'killall -9  -u root python3'
         ssh root@$remote_client3_ip 'killall -9  -u root python3'
      fi
      if [ ${i} == "2" ]; then
        ssh root@$remote_client1_ip 'killall -9  -u root python3'
        tc qdisc del dev $ethernet_interface_name root;
      fi
      if [ ${i} == "3" ]; then
         ssh root@$remote_client1_ip 'killall -9  -u root python3'
         ssh root@$remote_client2_ip 'killall -9  -u root python3'
         ssh root@$remote_client3_ip 'killall -9  -u root python3'
      fi
      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done