#!/bin/bash

wait_period=0
ethernet_interface_name='bond0'
main_sleep_time=10
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
    #                  50: "network", 51: "network", 52: "network", 53: "network", 54: "network", 55: "network",
    #                  56: "cpu", 57: "cpu", 58: "cpu"}
    #############################################################
    # run metric_collector with label value 0 for normal situation 0: "normal"
    python3 parallel_metric_collector.py 0 &
    sleep $main_sleep_time;
    killall -9 python3;
    killall -9 java;
    wait_period=$(($wait_period+60));
    sleep 5;

    #generate a random variable if it is even do the if part 1: "read" with 1 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 1 &
        sleep 5;
        python3 parallel_metric_collector.py 1 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi

    #generate a random variable if it is even do the if part 2: "read" with 2 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 2 &
        sleep 5;
        python3 parallel_metric_collector.py 2 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 4: "read" with 4 thread
    # number=$RANDOM
    number=0
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 4 &
        sleep 5;
        python3 parallel_metric_collector.py 4 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 8: "read" with 8 thread
    # number=$RANDOM
    number=0
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 8 &
        sleep 5;
        python3 parallel_metric_collector.py 8 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 12: "read" with 12 thread
    # number=$RANDOM
    number=0
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 12 &
        sleep 5;
        python3 parallel_metric_collector.py 12 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if part 16: "read" with 16 thread
    # number=$RANDOM
    number=0
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/read_test.py 16 &
        sleep 5;
        python3 parallel_metric_collector.py 16 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 17: "write" with 4 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 4 &
        sleep 5;
        python3 parallel_metric_collector.py 17 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
   #generate a random variable if it is even do the if 18: "write" with 8 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 8 &
        sleep 5;
        python3 parallel_metric_collector.py 18 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 19: "write" with 12 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 12 &
        sleep 5;
        python3 parallel_metric_collector.py 19 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 20: "write" with 16 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 16 &
        sleep 5;
        python3 parallel_metric_collector.py 20 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 21: "write" with 20 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 20 &
        sleep 5;
        python3 parallel_metric_collector.py 21 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 22: "write" with 24 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 24 &
        sleep 5;
        python3 parallel_metric_collector.py 22 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 23: "write" with 28 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 28 &
        sleep 5;
        python3 parallel_metric_collector.py 23 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 24: "write" with 32 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 32 &
        sleep 5;
        python3 parallel_metric_collector.py 24 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 25: "write" with 36 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 36 &
        sleep 5;
        python3 parallel_metric_collector.py 25 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 26: "write" with 40 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 40 &
        sleep 5;
        python3 parallel_metric_collector.py 26 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 27: "write" with 44 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 44 &
        sleep 5;
        python3 parallel_metric_collector.py 27 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 28: "write" with 48 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 48 &
        sleep 5;
        python3 parallel_metric_collector.py 28 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 29: "write" with 64 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 64 &
        sleep 5;
        python3 parallel_metric_collector.py 29 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 30: "write" with 72 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 72 &
        sleep 5;
        python3 parallel_metric_collector.py 30 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 31: "write" with 96 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 96 &
        sleep 5;
        python3 parallel_metric_collector.py 31 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
    #generate a random variable if it is even do the if 32: "write" with 128 thread
    # number=$RANDOM
    if [ $((number%2)) -eq 0 ]
    then
        python3 ../utilities/write_test.py 128 &
        sleep 5;
        python3 parallel_metric_collector.py 32 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
done
