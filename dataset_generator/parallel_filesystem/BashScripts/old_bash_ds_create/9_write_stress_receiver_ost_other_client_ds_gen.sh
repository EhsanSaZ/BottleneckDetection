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
    #############################################################
    #label_to_error = {0: "normal", 1: "read", 2: "read", 3: "read", 4: "read",
    #                  5: "read", 6: "read", 7: "read", 8: "read", 9: "read",
    #                  10: "read", 11: "read", 12: "read", 13: "read", 14: "read",
    #                  15: "read", 16: "read", 17: "write", 18: "write", 19: "write",
    #                  20: "write", 21: "write", 22: "write", 23: "write", 24: "write",
    #                  25: "write", 26: "write", 27: "write", 28: "write", 29: "write",
    #                  30: "write", 31: "write", 32: "write", 33: "cpu", 34: "io", 35: "mem",
    #                  36: "network", 37: "network", 38: "network", 39: "network",
    #                  40: "network", 41: "network", 42: "network", 43: "network", 44: "network",
    #                  45: "network", 46: "network", 47: "network", 48: "network", 49: "network",
    #                  50: "network", 51: "network", 52: "network", 53: "network", 54: "network", 55: "network",
    #                  56: "cpu", 57: "cpu", 58: "cpu"}
    #############################################################

    #generate a random variable if it is even do the if part 66: write stress to  receiver-side ost from from another client 4 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 66'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 4 &
      python3 parallel_metric_collector.py 66 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 67: write stress to  receiver-side ost from from another client 8 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 67'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 8 &
      python3 parallel_metric_collector.py 67 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 68: write stress to  receiver-side ost from from another client 16 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 68'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 16 &
      python3 parallel_metric_collector.py 68 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 69: write stress to  receiver-side ost from from another client 32 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 69'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 32 &
      python3 parallel_metric_collector.py 69 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 70: write stress to  receiver-side ost from from another client 48 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 70'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 48 &
      python3 parallel_metric_collector.py 70 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 71: write stress to  receiver-side ost from from another client 64 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 71'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 64 &
      python3 parallel_metric_collector.py 71 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 72: write stress to  receiver-side ost from from another client 96 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 72'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 96 &
      python3 parallel_metric_collector.py 72 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 73: write stress to  receiver-side ost from from another client 128 threads
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 73'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/receiverDataDir/diskWriteStress/ 128 &
      python3 parallel_metric_collector.py 73 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi

    round_counter=$(($round_counter+1));
done