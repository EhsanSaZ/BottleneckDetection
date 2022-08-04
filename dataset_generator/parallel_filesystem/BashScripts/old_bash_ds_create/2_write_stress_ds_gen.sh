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

    #generate a random variable if it is even do the if 17: "write" with 4 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 17'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 4 &
      python3 parallel_metric_collector.py 17 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 18: "write" with 8 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 18'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 8 &
      python3 parallel_metric_collector.py 18 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 19: "write" with 12 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 19'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 12 &
      python3 parallel_metric_collector.py 19 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 20: "write" with 16 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 20'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 16 &
      python3 parallel_metric_collector.py 20 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 21: "write" with 20 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 21'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 20 &
      python3 parallel_metric_collector.py 21 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 22: "write" with 24 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 22'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 24 &
      python3 parallel_metric_collector.py 22 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 23: "write" with 28 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 23'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 28 &
      python3 parallel_metric_collector.py 23 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 24: "write" with 32 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 24'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 32 &
      python3 parallel_metric_collector.py 24 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 25: "write" with 36 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 25'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 36 &
      python3 parallel_metric_collector.py 25 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 26: "write" with 40 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 26'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 40 &
      python3 parallel_metric_collector.py 26 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 27: "write" with 44 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 27'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 44 &
      python3 parallel_metric_collector.py 27 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 28: "write" with 48 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 28'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 48 &
      python3 parallel_metric_collector.py 28 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 29: "write" with 64 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 29'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 64 &
      python3 parallel_metric_collector.py 29 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 30: "write" with 72 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 30'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 72 &
      python3 parallel_metric_collector.py 30 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 31: "write" with 96 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 31'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 96 &
      python3 parallel_metric_collector.py 31 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 32: "write" with 128 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py 32'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ./AgentMetricCollector/DiskRWStress/write_test.py /lustre/dataDir/diskWriteStress/ 128 &
      python3 parallel_metric_collector.py 32 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi

    round_counter=$(($round_counter+1));
done
