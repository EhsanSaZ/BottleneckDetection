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
}
kill_all_java_python3_processes(){
    killall -9  -u $user_name iperf3;

    ssh root@$receiver_ip 'killall -9  -u root python3'
    ssh root@$receiver_ip 'killall -9  -u root java'
    ssh root@$receiver_ip 'killall -9  -u root iperf3'

    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;
}

levels=(["52"]=5205 ["53"]=5210 ["54"]=5215)

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
      ssh root@$receiver_ip "for i in {5201..5205}; do iperf3 -s -p \${i} >> /dev/null & done"&
      sleep 10;

      if $limited_bw
      then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 30ms;
      fi


      if [ ${i} == "52" ]; then
        ssh root@$remote_client1_ip "for j in {5201..5205}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
      fi
      if [ ${i} == "53" ]; then
        ssh root@$remote_client1_ip "for j in {5201..5205}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
        ssh root@$remote_client2_ip "for j in {5206..5210}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
      fi
      if [ ${i} == "54" ]; then
        ssh root@$remote_client1_ip "for j in {5201..5205}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
        ssh root@$remote_client2_ip "for j in {5206..5210}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
        ssh root@$remote_client3_ip "for j in {5211..5215}; do iperf3 -c ${receiver_ip} -t 10000 -p \${j}>>/dev/null & done" &
      fi
      echo "Run the Java client on sender side and Start metric collector agent";
      sleep 30;
      python3 ../../AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 1 -jlp 50521 -jtl ${label}&

      sleep $main_sleep_time;
      kill_all_java_python3_processes

      if [ ${i} == "52" ]; then
         ssh root@$remote_client1_ip 'killall -9  -u root iperf3'
      fi
      if [ ${i} == "53" ]; then
         ssh root@$remote_client1_ip 'killall -9  -u root iperf3'
         ssh root@$remote_client2_ip 'killall -9  -u root iperf3'
      fi
      if [ ${i} == "54" ]; then
         ssh root@$remote_client1_ip 'killall -9  -u root iperf3'
         ssh root@$remote_client2_ip 'killall -9  -u root iperf3'
         ssh root@$remote_client3_ip 'killall -9  -u root iperf3'
      fi

      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
      sleep 5;
    done
    round_counter=$(($round_counter+1));
done
