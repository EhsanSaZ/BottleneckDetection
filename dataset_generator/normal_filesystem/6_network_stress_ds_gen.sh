#!/bin/bash

round_counter=1
ethernet_interface_name='enp0s31f6'
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

    #generate a random variable if it is even do the if part 36: "network" loss 0.5%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 36'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem loss 0.5%;
      sleep 5;
      python3 metric_collector.py 36 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 37: "network" loss 0.1%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 37'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem loss 0.1%;
      sleep 5;
      python3 metric_collector.py 37 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 38: "network" loss 0.05%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 38'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem loss 0.05%;
      sleep 5;
      python3 metric_collector.py 38 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 39: "network" loss 1%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 39'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem loss 1%;
      sleep 5;
      python3 metric_collector.py 39 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 40: "network" delay 0.1ms 0.1
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 40'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 0.1ms distribution normal;
      sleep 5;
      python3 metric_collector.py 40 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 41: "network" delay 0.1ms 0.5ms
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 41'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 0.5ms distribution normal;
      sleep 5;
      python3 metric_collector.py 41 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 42: "network" delay 0.1ms 1ms
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 42'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 1ms distribution normal;
      sleep 5;
      python3 metric_collector.py 42 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 43: "network" delay 0.1ms 2ms
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 43'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 2ms distribution normal;
      sleep 5;
      python3 metric_collector.py 43 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 44: "network" duplicate 10%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 44'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem duplicate 10%;
      sleep 5;
      python3 metric_collector.py 44 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 45: "network" duplicate 15%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 45'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem duplicate 15%;
      sleep 5;
      python3 metric_collector.py 45 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 46: "network" duplicate 20%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 46'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem duplicate 20%;
      sleep 5;
      python3 metric_collector.py 46 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 47: "network" duplicate 25%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 47'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem duplicate 25%;
      sleep 5;
      python3 metric_collector.py 47 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 48: "network" corrupt 0.5%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 48'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem corrupt 0.5%;
      sleep 5;
      python3 metric_collector.py 48 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 49: "network" corrupt 0.1%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 49'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem corrupt 0.1%;
      sleep 5;
      python3 metric_collector.py 49 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 50: "network" corrupt 0.05%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 50'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem corrupt 0.05%;
      sleep 5;
      python3 metric_collector.py 50 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 51: "network" corrupt 1%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 51'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem corrupt 1%;
      sleep 5;
      python3 metric_collector.py 51 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 52: "network" reorder 10%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 52'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem reorder 10% delay 1ms;
      sleep 5;
      python3 metric_collector.py 52 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 53: "network" reorder 15%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 53'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem reorder 15% delay 1ms;
      sleep 5;
      python3 metric_collector.py 53 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 54: "network" reorder 20%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 54'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem reorder 20% delay 1ms;
      sleep 5;
      python3 metric_collector.py 54 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    #generate a random variable if it is even do the if part 55: "network" reorder 25%
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
      clear_all_caches
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip 'python3 /home/a/AgentMetricCollector/remote_metric_collector.py 55'&
      sleep 5;
      echo "Start collecting metrics on sender side";
      tc qdisc add dev $ethernet_interface_name root netem reorder 25% delay 1ms;
      sleep 5;
      python3 metric_collector.py 55 &
      sleep $main_sleep_time;
      tc qdisc del dev $ethernet_interface_name root;
      kill_all_java_python3_processes
      sleep 5;
    fi
    round_counter=$(($round_counter+1));
done