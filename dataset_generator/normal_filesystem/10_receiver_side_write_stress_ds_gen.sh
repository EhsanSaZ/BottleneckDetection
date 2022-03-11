#!/bin/bash

round_counter=1
ethernet_interface_name=''
user_name='root'
receiver_remote_client_ip=134.197.95.46
main_sleep_time=30

clear_all_caches() {
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
    #generate a random variable if it is even do the if 74: "write" with 4 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 74'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 4'&
      python3 metric_collector.py 74 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 75: "write" with 8 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 75'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 8'&
      python3 metric_collector.py 75 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 76: "write" with 16 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 76'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 16'&
      python3 metric_collector.py 76 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 77: "write" with 24 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 77'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 24'&
      python3 metric_collector.py 77 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 78: "write" with 32 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 78'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 32'&
      python3 metric_collector.py 78 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 79: "write" with 64 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 79'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 64'&
      python3 metric_collector.py 79 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 80: "write" with 96 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 80'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 96'&
      python3 metric_collector.py 80 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if 81: "write" with 128 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 81'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/DiskRWStress/write_test.py /home/a/receiverDataDir/diskWriteStress/ 128'&
      python3 metric_collector.py 81 &
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      sleep 5;
    fi

    round_counter=$(($round_counter+1));
done