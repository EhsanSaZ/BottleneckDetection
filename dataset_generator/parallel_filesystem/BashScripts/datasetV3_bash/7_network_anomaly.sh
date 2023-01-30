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
}
kill_all_java_python3_processes(){
    ssh root@$receiver_ip 'killall -9  -u root python3'
    ssh root@$receiver_ip 'killall -9  -u root java'

    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;
}
# network_anomaly_network_duplicate
levels=(["21"]=15 ["22"]=25 ["23"]=40 ["24"]=60)

while true
do
    printf "\n"
    echo "round number ${round_counter}"
    if [ $round_counter -gt $max_round_number ];then
       break
    fi
    for i in "${!levels[@]}"; do
      clear_all_caches
      label=$i
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_ip "python3 /users/Ehsan/AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 2 -jsp 50505 -jtl ${label}"&
      if $limited_bw
      then
        tc qdisc add dev $ethernet_interface_name root netem duplicate ${levels[$i]}% rate ${network_bw};
      else
        tc qdisc add dev $ethernet_interface_name root netem duplicate ${levels[$i]}%;
      fi
      sleep 8;
      echo "Run the Java client on sender side and Start metric collector agent";
      python3 ../../AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 1 -jlp 50521 -jtl ${label}&

      sleep $main_sleep_time;
      kill_all_java_python3_processes
      tc qdisc del dev $ethernet_interface_name root;
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done
