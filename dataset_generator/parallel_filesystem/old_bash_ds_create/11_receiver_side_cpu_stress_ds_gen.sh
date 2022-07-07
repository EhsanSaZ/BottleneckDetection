#!/bin/bash

round_counter=1
ethernet_interface_name='enp1s0f0'
user_name='root'
receiver_remote_client_ip=10.10.1.5
sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3
main_sleep_time=30

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
while true
do
    printf "\n"
    echo "round number ${round_counter}"
    if [ $round_counter -gt 6 ];then
       break
    fi

    #generate a random variable if it is even do the if part 82: "cpu" 10 % cpu load on all cores
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 82'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'stress-ng -c 0 -l 10'&
      sleep 5;
      python3 parallel_metric_collector.py 82 &
      sleep $main_sleep_time;
      ssh root@$receiver_remote_client_ip 'killall -9 stress-ng';
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 83: "cpu" 30 % cpu load on all cores
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 83'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'stress-ng -c 0 -l 30'&
      sleep 5;
      python3 parallel_metric_collector.py 83 &
      sleep $main_sleep_time;
      ssh root@$receiver_remote_client_ip 'killall -9 stress-ng';
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 84: "cpu" 70 % cpu load on all cores
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 84'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'stress-ng -c 0 -l 70'&
      sleep 5;
      python3 parallel_metric_collector.py 84 &
      sleep $main_sleep_time;
      ssh root@$receiver_remote_client_ip 'killall -9 stress-ng';
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 85: "cpu" 100 % cpu load on all cores
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 85'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'stress-ng -c 0 -l 100'&
      sleep 5;
      python3 parallel_metric_collector.py 85 &
      sleep $main_sleep_time;
      ssh root@$receiver_remote_client_ip 'killall -9 stress-ng';
      kill_all_java_python3_processes
      sleep 5;
    fi

    round_counter=$(($round_counter+1));
done