#!/bin/bash

wait_period=0
ethernet_interface_name='enp0s31f6'
main_sleep_time=15
while true
do
    echo "wait period ${wait_period}"
    if [ $wait_period -gt 36000 ];then
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
    #                  50: "network", 51: "network", 52: "network", 53: "network", 54: "network", 55: "network"}
    #############################################################
    # run metric_collector with label value 0 for normal situation 0: "normal"
    python3 metric_collector.py 0 &
    sleep $main_sleep_time;
    killall -9 python3;
    killall -9 java;
    wait_period=$(($wait_period+60));
    sleep 5;

    #generate a random variable if it is even do the if part 1: "read" with 1 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 1 &
        sleep 5;
        python3 metric_collector.py 1 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 2: "read" with 2 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 2 &
        sleep 5;
        python3 metric_collector.py 2 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 3: "read" with 3 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 3 &
        sleep 5;
        python3 metric_collector.py 3 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 4: "read" with 4 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 4 &
        sleep 5;
        python3 metric_collector.py 4 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 5: "read" with 5 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 5 &
        sleep 5;
        python3 metric_collector.py 5 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 6: "read" with 6 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 6 &
        sleep 5;
        python3 metric_collector.py 6 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 7: "read" with 7 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 7 &
        sleep 5;
        python3 metric_collector.py 7 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 8: "read" with 8 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 8 &
        sleep 5;
        python3 metric_collector.py 8 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 9: "read" with 9 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 9 &
        sleep 5;
        python3 metric_collector.py 9 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 10: "read" with 10 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 10 &
        sleep 5;
        python3 metric_collector.py 10 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 11: "read" with 11 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 11 &
        sleep 5;
        python3 metric_collector.py 11 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 12: "read" with 12 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 12 &
        sleep 5;
        python3 metric_collector.py 12 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 13: "read" with 13 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 13 &
        sleep 5;
        python3 metric_collector.py 13 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 14: "read" with 14 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 14 &
        sleep 5;
        python3 metric_collector.py 14 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 15: "read" with 15 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 15 &
        sleep 5;
        python3 metric_collector.py 15 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 16: "read" with 16 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 16 &
        sleep 5;
        python3 metric_collector.py 16 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 17: "write" with 4 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 4 &
        sleep 5;
        python3 metric_collector.py 17 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 18: "write" with 8 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 8 &
        sleep 5;
        python3 metric_collector.py 18 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 19: "write" with 12 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 12 &
        sleep 5;
        python3 metric_collector.py 19 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 20: "write" with 16 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 16 &
        sleep 5;
        python3 metric_collector.py 20 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 21: "write" with 20 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 20 &
        sleep 5;
        python3 metric_collector.py 21 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 22: "write" with 24 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 24 &
        sleep 5;
        python3 metric_collector.py 22 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 23: "write" with 28 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 28 &
        sleep 5;
        python3 metric_collector.py 23 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 24: "write" with 32 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 32 &
        sleep 5;
        python3 metric_collector.py 24 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 25: "write" with 36 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 36 &
        sleep 5;
        python3 metric_collector.py 25 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 26: "write" with 40 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 40 &
        sleep 5;
        python3 metric_collector.py 26 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 27: "write" with 44 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 44 &
        sleep 5;
        python3 metric_collector.py 27 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 28: "write" with 48 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 48 &
        sleep 5;
        python3 metric_collector.py 28 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 29: "write" with 64 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 64 &
        sleep 5;
        python3 metric_collector.py 29 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 30: "write" with 72 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 72 &
        sleep 5;
        python3 metric_collector.py 30 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 31: "write" with 96 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 96 &
        sleep 5;
        python3 metric_collector.py 31 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 32: "write" with 128 thread
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 128 &
        sleep 5;
        python3 metric_collector.py 32 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 33: "cpu" 10 % cpu load on all cores
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        stress-ng -c 0 -l 10 &
        sleep 5;
        python3 metric_collector.py 33 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 56: "cpu" 30 % cpu load on all cores
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        stress-ng -c 0 -l 30 &
        sleep 5;
        python3 metric_collector.py 56 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 57: "cpu" 70 % cpu load on all cores
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        stress-ng -c 0 -l 70 &
        sleep 5;
        python3 metric_collector.py 57 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 58: "cpu" 100 % cpu load on all cores
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        stress-ng -c 0 -l 100 &
        sleep 5;
        python3 metric_collector.py 58 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 34: "io"
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        stress -i 10 &
        sleep 5;
        python3 metric_collector.py 34 &
        sleep $main_sleep_time;
        killall -9 stress;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 35: "mem"
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        # T ODO check if with or with out "" is true
        stress-ng --vm-bytes "$(awk '/MemAvailable/{printf "%d\n", $2 * 0.98;}' < /proc/meminfo)"k --vm-keep -m 10  &
        sleep 5;
        python3 metric_collector.py 35 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 36: "network" loss 0.5%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem loss 0.5%;
        sleep 5;
        python3 metric_collector.py 36 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 37: "network" loss 0.1%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem loss 0.1%;
        sleep 5;
        python3 metric_collector.py 37 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 38: "network" loss 0.05%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem loss 0.05%;
        sleep 5;
        python3 metric_collector.py 38 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 39: "network" loss 1%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem loss 1%;
        sleep 5;
        python3 metric_collector.py 39 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 40: "network" delay 0.1ms 0.1
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 0.1   distribution normal;
        sleep 5;
        python3 metric_collector.py 40 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 41: "network" delay 0.1ms 0.5ms
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 0.5ms distribution normal;
        sleep 5;
        python3 metric_collector.py 41 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 42: "network" delay 0.1ms 1ms
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 1ms distribution normal;
        sleep 5;
        python3 metric_collector.py 42 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 43: "network" delay 0.1ms 2ms
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 2ms distribution normal;
        sleep 5;
        python3 metric_collector.py 43 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 44: "network" duplicate 10%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem duplicate 10%;
        sleep 5;
        python3 metric_collector.py 44 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 45: "network" duplicate 15%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem duplicate 15%;
        sleep 5;
        python3 metric_collector.py 45 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 46: "network" duplicate 20%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem duplicate 20%;
        sleep 5;
        python3 metric_collector.py 46 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 47: "network" duplicate 25%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem duplicate 25%;
        sleep 5;
        python3 metric_collector.py 47 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 48: "network" corrupt 0.5%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem corrupt 0.5%;
        sleep 5;
        python3 metric_collector.py 48 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 49: "network" corrupt 0.1%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem corrupt 0.1%;
        sleep 5;
        python3 metric_collector.py 49 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 50: "network" corrupt 0.05%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem corrupt 0.05%;
        sleep 5;
        python3 metric_collector.py 50 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 51: "network" corrupt 1%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem corrupt 1%;
        sleep 5;
        python3 metric_collector.py 51 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 52: "network" reorder 10%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem reorder 10% delay 1ms;
        sleep 5;
        python3 metric_collector.py 52 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 53: "network" reorder 15%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem reorder 15% delay 1ms;
        sleep 5;
        python3 metric_collector.py 53 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 54: "network" reorder 20%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem reorder 20% delay 1ms;
        sleep 5;
        python3 metric_collector.py 54 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 55: "network" reorder 25%
    number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        tc qdisc add dev $ethernet_interface_name root netem reorder 25% delay 1ms;
        sleep 5;
        python3 metric_collector.py 55 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
#    #generate a random variable if it is even do the if
#    number=$RANDOM
#    if [ $((number%2)) -eq 0 ]
#    then
#        tc qdisc add dev $ethernet_interface_name root tbf rate 600Mbit burst 32Mbit limit 30000;
#        sleep 5;
#        python3 metric_collector.py 56 &
#        sleep $main_sleep_time;
#        killall -9 python3;
#        killall -9 java;
#        wait_period=$(($wait_period+60));
#        tc qdisc del dev $ethernet_interface_name root;
#        sleep 5;
#    fi
#    number=$RANDOM
#    if [ $((number%2)) -eq 0 ]
#    then
#        tc qdisc add dev $ethernet_interface_name root tbf rate 500Mbit burst 32Mbit limit 30000;
#        sleep 5;
#        python3 metric_collector.py 57 &
#        sleep $main_sleep_time;
#        killall -9 python3;
#        killall -9 java;
#        wait_period=$(($wait_period+60));
#        tc qdisc del dev $ethernet_interface_name root;
#        sleep 5;
#    fi
#    number=$RANDOM
#    if [ $((number%2)) -eq 0 ]
#    then
#        tc qdisc add dev $ethernet_interface_name root tbf rate 550Mbit burst 32Mbit limit 30000;
#        sleep 5;
#        python3 metric_collector.py 58 &
#        sleep $main_sleep_time;
#        killall -9 python3;
#        killall -9 java;
#        wait_period=$(($wait_period+60));
#        tc qdisc del dev $ethernet_interface_name root;
#        sleep 5;
#    fi
#    number=$RANDOM
#    if [ $((number%2)) -eq 0 ]
#    then
#        tc qdisc add dev $ethernet_interface_name root tbf rate 580Mbit burst 32Mbit limit 30000;
#        sleep 5;
#        python3 metric_collector.py 59 &
#        sleep $main_sleep_time;
#        killall -9 python3;
#        killall -9 java;
#        wait_period=$(($wait_period+60));
#        tc qdisc del dev $ethernet_interface_name root;
#        sleep 5;
#    fi
done
