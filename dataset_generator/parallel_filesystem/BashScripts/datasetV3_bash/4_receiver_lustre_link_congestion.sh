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

#remote_client1_ip=10.10.2.3
#remote_client2_ip=10.10.2.4
#remote_client3_ip=10.10.2.5

ethernet_interface_name='enp6s0f1'
network_bw=1024mbit
limited_bw=true


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
# Lustre_Link_congestion_on_receiver_side
#congestions=([1]="Lustre_Link_congestion_on_receiver_side_1" [2]="Lustre_Link_congestion_on_receiver_side_2"
#[3]="Lustre_Link_congestion_on_receiver_side_3")

#CONGESTION LEVELS FOR SSD DISK
#congestions=([6]="10" [8]="11" [10]="12")
#CONGESTION LEVELS FOR HDD DISK
congestions=([10]="10" [12]="11" [14]="12")

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
      echo "Run the java server on receiver side and start metric collector agent\n";
      ssh root@$receiver_ip "python3 /users/Ehsan/AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 2 -jsp 50505 -jtl ${label}"&
      if $limited_bw
      then
#        sudo tc qdisc add dev $ethernet_interface_name root netem rate ${network_bw};
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 30ms;
      fi
      sleep 8;

      if [ ${i} == "10" ]; then
         echo "Congestion lnk with -P level 1"
         ssh root@$server3 "iperf3 -s >> /dev/null" & sleep 5;ssh root@$receiver_ip "iperf3 -c ${server3} -t 10000 -P ${i} >> /dev/null"&
      fi
      if [ ${i} == "12" ]; then
         echo "Congestion lnk with -P level 2"
         ssh root@$server3 "iperf3 -s >> /dev/null" & sleep 5;ssh root@$receiver_ip "iperf3 -c ${server3} -t 10000 -P ${i} >> /dev/null"&
      fi
      if [ ${i} == "14" ]; then
         echo "Congestion lnk with -P level 3"
         ssh root@$server3 "iperf3 -s >> /dev/null" & sleep 5;ssh root@$receiver_ip "iperf3 -c ${server3} -t 10000 -P ${i} >> /dev/null"&
      fi
      sleep 5;
      echo "Run the Java client on sender side and Start metric collector agent";
      python3 ../../AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 1 -jlp 50521 -jtl ${label}&

      sleep $main_sleep_time;
      kill_all_java_python3_processes

      ssh root@$receiver_ip "killall -9 iperf3";
      ssh root@server3 "killall -9 iperf3";

      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done